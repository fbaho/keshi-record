/**
 * 课时记录 App - 主应用
 * Vue 3 + LocalStorage
 */

const { createApp, ref, reactive, computed, onMounted, watch, nextTick } = Vue;

createApp({
  setup() {
    // ===== 全局状态 =====
    const currentPage = ref('home');
    const toastMsg = ref('');
    let toastTimer = null;

    // 数据
    const students = ref([]);
    const records = ref([]);
    const summary = ref({});

    // 弹窗状态
    const showAddStudent = ref(false);
    const showStudentDetail = ref(false);
    const showEditStudent = ref(false);
    const currentStudent = ref(null);
    const currentStudentRecords = ref([]);

    // 消课状态
    const consumeDate = ref(new Date().toISOString().slice(0, 10));
    const consumeList = ref([]); // [{ studentId, selected, hours }]

    // 统计状态
    const statsRange = ref('month'); // week / month / all
    const statsData = ref(null);

    // ===== 工具函数 =====
    function showToast(msg) {
      toastMsg.value = msg;
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { toastMsg.value = ''; }, 2000);
    }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return `${d.getMonth() + 1}月${d.getDate()}日`;
    }

    function formatDateFull(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
    }

    function getAvatarChar(name) {
      if (!name) return '?';
      return name.charAt(0).toUpperCase();
    }

    function formatMoney(n) {
      return Number(n || 0).toFixed(2);
    }

    // ===== 数据加载 =====
    function loadData() {
      Storage.init();
      students.value = Storage.getStudents();
      records.value = Storage.getRecords();
      summary.value = Storage.getSummary();
    }

    // ===== 页面切换 =====
    function switchPage(page) {
      currentPage.value = page;
      if (page === 'home') loadData();
      if (page === 'consume') initConsumeList();
      if (page === 'stats') loadStats();
    }

    // ===== 学员管理 =====
    const newStudent = reactive({
      name: '',
      totalAmount: '',
      totalHours: '',
      notes: ''
    });

    const computedPerClassFee = computed(() => {
      const amt = parseFloat(newStudent.totalAmount);
      const hrs = parseFloat(newStudent.totalHours);
      if (!amt || !hrs || hrs <= 0) return 0;
      return (amt / hrs).toFixed(2);
    });

    function resetNewStudent() {
      newStudent.name = '';
      newStudent.totalAmount = '';
      newStudent.totalHours = '';
      newStudent.notes = '';
    }

    function handleAddStudent() {
      if (!newStudent.name.trim()) {
        showToast('请输入学员姓名');
        return;
      }
      const amt = parseFloat(newStudent.totalAmount);
      const hrs = parseFloat(newStudent.totalHours);
      if (!amt || amt <= 0) {
        showToast('请输入有效的总金额');
        return;
      }
      if (!hrs || hrs <= 0) {
        showToast('请输入有效的总课时');
        return;
      }

      Storage.addStudent({
        name: newStudent.name.trim(),
        totalAmount: amt,
        totalHours: hrs,
        notes: newStudent.notes.trim()
      });

      resetNewStudent();
      showAddStudent.value = false;
      loadData();
      showToast('学员添加成功');
    }

    function openStudentDetail(student) {
      currentStudent.value = { ...student };
      currentStudentRecords.value = Storage.getRecordsByStudent(student.id);
      showStudentDetail.value = true;
    }

    function handleDeleteStudent() {
      if (!currentStudent.value) return;
      if (!confirm(`确认删除学员「${currentStudent.value.name}」？\n该学员的所有消课记录将一并删除，此操作不可撤销。`)) return;
      Storage.deleteStudent(currentStudent.value.id);
      showStudentDetail.value = false;
      loadData();
      showToast('已删除学员');
    }

    // 编辑学员
    const editForm = reactive({
      name: '',
      totalAmount: '',
      totalHours: '',
      notes: ''
    });

    function openEditStudent() {
      if (!currentStudent.value) return;
      editForm.name = currentStudent.value.name;
      editForm.totalAmount = currentStudent.value.totalAmount;
      editForm.totalHours = currentStudent.value.totalHours;
      editForm.notes = currentStudent.value.notes || '';
      showEditStudent.value = true;
    }

    function handleEditStudent() {
      if (!currentStudent.value) return;
      if (!editForm.name.trim()) {
        showToast('请输入学员姓名');
        return;
      }
      const amt = parseFloat(editForm.totalAmount);
      const hrs = parseFloat(editForm.totalHours);
      if (!amt || amt <= 0) {
        showToast('请输入有效的总金额');
        return;
      }
      if (!hrs || hrs <= 0) {
        showToast('请输入有效的总课时');
        return;
      }

      const updated = Storage.updateStudent(currentStudent.value.id, {
        name: editForm.name.trim(),
        totalAmount: amt,
        totalHours: hrs,
        notes: editForm.notes.trim()
      });

      currentStudent.value = { ...updated };
      showEditStudent.value = false;
      loadData();
      showToast('修改成功');
    }

    // ===== 消课 =====
    function initConsumeList() {
      consumeList.value = students.value.map(s => ({
        studentId: s.id,
        name: s.name,
        perClassFee: s.perClassFee,
        remainingHours: s.remainingHours,
        selected: false,
        hours: 1
      }));
    }

    const selectedConsumptions = computed(() => {
      return consumeList.value.filter(c => c.selected);
    });

    const consumeSummary = computed(() => {
      const selected = selectedConsumptions.value;
      const totalHours = selected.reduce((s, c) => s + c.hours, 0);
      const totalAmount = selected.reduce((s, c) => s + c.hours * c.perClassFee, 0);
      return {
        count: selected.length,
        totalHours,
        totalAmount: totalAmount.toFixed(2)
      };
    });

    function changeHours(item, delta) {
      const newVal = item.hours + delta;
      if (newVal < 0.5) return;
      if (newVal > item.remainingHours) {
        showToast(`剩余课时不足（剩余 ${item.remainingHours} 课时）`);
        return;
      }
      item.hours = newVal;
    }

    function handleConsume() {
      const selected = selectedConsumptions.value;
      if (selected.length === 0) {
        showToast('请至少选择一名学员');
        return;
      }

      // 检查课时是否足够
      for (const item of selected) {
        if (item.hours > item.remainingHours) {
          showToast(`${item.name} 剩余课时不足`);
          return;
        }
      }

      const consumptions = selected.map(c => ({
        studentId: c.studentId,
        hours: c.hours,
        date: consumeDate.value,
        note: ''
      }));

      Storage.addRecords(consumptions);
      loadData();
      initConsumeList();
      showToast(`成功消课 ${selected.length} 人，共 ${consumeSummary.value.totalHours} 课时`);
    }

    // 删除消课记录
    function handleDeleteRecord(recordId) {
      if (!confirm('确认删除这条消课记录？\n课时和金额将自动回退。')) return;
      Storage.deleteRecord(recordId);
      if (currentStudent.value) {
        currentStudent.value = Storage.getStudent(currentStudent.value.id);
        currentStudentRecords.value = Storage.getRecordsByStudent(currentStudent.value.id);
      }
      loadData();
      showToast('记录已删除');
    }

    // ===== 统计 =====
    function loadStats() {
      const now = new Date();
      let startDate, endDate;
      endDate = now.toISOString().slice(0, 10);

      if (statsRange.value === 'week') {
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() - now.getDay() + 1); // 周一
        startDate = weekStart.toISOString().slice(0, 10);
      } else if (statsRange.value === 'month') {
        startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
      } else {
        startDate = '2000-01-01';
      }

      statsData.value = Storage.getStatsByDateRange(startDate, endDate);
      nextTick(() => renderChart());
    }

    function renderChart() {
      if (!statsData.value || !statsData.value.byDate.length) return;

      const canvas = document.getElementById('statsChart');
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      const byDate = [...statsData.value.byDate].reverse().slice(-14); // 最近14条

      // 清空画布
      const dpr = window.devicePixelRatio || 1;
      const width = canvas.parentElement.clientWidth - 32;
      const height = 240;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.scale(dpr, dpr);

      // 绘制柱状图
      const padding = { top: 20, right: 10, bottom: 30, left: 40 };
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxVal = Math.max(...byDate.map(d => d.amount), 1);
      const barW = Math.max(8, chartW / byDate.length - 6);

      // Y轴刻度
      ctx.fillStyle = '#999';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      for (let i = 0; i <= 4; i++) {
        const y = padding.top + chartH - (chartH * i / 4);
        const val = (maxVal * i / 4).toFixed(0);
        ctx.fillText(val, padding.left - 6, y + 3);
        // 网格线
        ctx.strokeStyle = '#F0F0F0';
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
      }

      // 柱子
      byDate.forEach((d, i) => {
        const x = padding.left + (chartW / byDate.length) * i + 3;
        const barH = (d.amount / maxVal) * chartH;
        const y = padding.top + chartH - barH;

        // 渐变
        const grad = ctx.createLinearGradient(0, y, 0, padding.top + chartH);
        grad.addColorStop(0, '#07C160');
        grad.addColorStop(1, '#06AD56');
        ctx.fillStyle = grad;

        // 圆角矩形
        const r = Math.min(4, barW / 2);
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + barW - r, y);
        ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
        ctx.lineTo(x + barW, y + barH);
        ctx.lineTo(x, y + barH);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.fill();

        // X轴日期
        ctx.fillStyle = '#999';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        const dateLabel = d.date.slice(5).replace('-', '/');
        ctx.fillText(dateLabel, x + barW / 2, height - padding.bottom + 14);
      });
    }

    // ===== 数据导出 =====
    function exportExcel() {
      const allStudents = Storage.getStudents();
      const allRecords = Storage.getRecords();

      if (allStudents.length === 0) {
        showToast('暂无数据可导出');
        return;
      }

      // 构建 CSV 内容
      let csv = '\uFEFF'; // BOM for Excel

      // === 学员汇总表 ===
      csv += '=== 学员汇总表 ===\n';
      csv += '姓名,总金额,总课时,课时单价,已消耗课时,剩余课时,已收金额(未消课),已消耗金额,消课进度(%),创建日期\n';
      allStudents.forEach(s => {
        const progress = s.totalHours > 0 ? (s.consumedHours / s.totalHours * 100).toFixed(1) : 0;
        csv += `${s.name},${s.totalAmount},${s.totalHours},${s.perClassFee},${s.consumedHours},${s.remainingHours},${s.receivedAmount},${s.consumedAmount},${progress},${s.createdAt.slice(0, 10)}\n`;
      });

      csv += '\n';

      // === 消课明细表 ===
      csv += '=== 消课明细表 ===\n';
      csv += '日期,学员姓名,消课课时,课时单价,消课金额,备注\n';
      allRecords.sort((a, b) => b.date.localeCompare(a.date)).forEach(r => {
        csv += `${r.date},${r.studentName},${r.hours},${r.perClassFee},${r.amount},${r.note || ''}\n`;
      });

      csv += '\n';

      // === 全局汇总 ===
      const sum = Storage.getSummary();
      csv += '=== 全局汇总 ===\n';
      csv += `总学员数,${sum.totalStudents}\n`;
      csv += `总已收金额(未消课),${sum.totalReceived}\n`;
      csv += `总已消耗金额,${sum.totalConsumed}\n`;
      csv += `总已消耗课时,${sum.totalConsumedHours}\n`;
      csv += `总剩余课时,${sum.totalRemainingHours}\n`;
      csv += `总消课记录数,${sum.totalRecords}\n`;

      // 下载
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `课时记录_${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      showToast('导出成功');
    }

    // ===== 计算属性 =====
    const recentRecords = computed(() => {
      return [...records.value]
        .sort((a, b) => b.id.localeCompare(a.id))
        .slice(0, 10);
    });

    const todayRecords = computed(() => {
      const today = new Date().toISOString().slice(0, 10);
      return records.value.filter(r => r.date === today);
    });

    const sortedStudents = computed(() => {
      return [...students.value].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    });

    const lowHoursStudents = computed(() => {
      return students.value.filter(s => s.remainingHours <= 3 && s.remainingHours > 0);
    });

    // ===== 生命周期 =====
    onMounted(() => {
      loadData();
    });

    return {
      // 状态
      currentPage,
      toastMsg,
      students,
      records,
      summary,
      showAddStudent,
      showStudentDetail,
      showEditStudent,
      currentStudent,
      currentStudentRecords,
      consumeDate,
      consumeList,
      statsRange,
      statsData,
      newStudent,
      computedPerClassFee,
      editForm,
      // 计算属性
      selectedConsumptions,
      consumeSummary,
      recentRecords,
      todayRecords,
      sortedStudents,
      lowHoursStudents,
      // 方法
      showToast,
      formatDate,
      formatDateFull,
      getAvatarChar,
      formatMoney,
      switchPage,
      loadData,
      resetNewStudent,
      handleAddStudent,
      openStudentDetail,
      handleDeleteStudent,
      openEditStudent,
      handleEditStudent,
      initConsumeList,
      changeHours,
      handleConsume,
      handleDeleteRecord,
      loadStats,
      exportExcel
    };
  }
}).mount('#app');

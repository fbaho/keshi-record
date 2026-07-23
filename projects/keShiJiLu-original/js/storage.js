/**
 * 课时记录 App - 数据存储层
 * 基于 localStorage 的本地数据持久化
 */

const DB_KEY = 'keshi_app_data';

const Storage = {
  /**
   * 初始化数据结构
   */
  init() {
    const existing = this.load();
    if (!existing) {
      const data = {
        students: [],
        records: [],
        version: '1.0.0'
      };
      this.save(data);
      return data;
    }
    return existing;
  },

  /**
   * 加载全部数据
   */
  load() {
    try {
      const raw = localStorage.getItem(DB_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (e) {
      console.error('数据加载失败:', e);
      return null;
    }
  },

  /**
   * 保存全部数据
   */
  save(data) {
    try {
      localStorage.setItem(DB_KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      console.error('数据保存失败:', e);
      return false;
    }
  },

  // ========== 学员相关 ==========

  /**
   * 获取所有学员
   */
  getStudents() {
    const data = this.load();
    return data ? data.students : [];
  },

  /**
   * 获取单个学员
   */
  getStudent(id) {
    const students = this.getStudents();
    return students.find(s => s.id === id);
  },

  /**
   * 新增学员
   * @param {Object} student - { name, totalAmount, totalHours, notes }
   */
  addStudent(student) {
    const data = this.load();
    const perClassFee = student.totalHours > 0
      ? +(student.totalAmount / student.totalHours).toFixed(2)
      : 0;

    const newStudent = {
      id: 's_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
      name: student.name,
      totalAmount: +student.totalAmount,
      totalHours: +student.totalHours,
      perClassFee: perClassFee,
      consumedHours: 0,
      remainingHours: +student.totalHours,
      receivedAmount: +student.totalAmount,
      consumedAmount: 0,
      notes: student.notes || '',
      createdAt: new Date().toISOString()
    };

    data.students.push(newStudent);
    this.save(data);
    return newStudent;
  },

  /**
   * 更新学员信息
   */
  updateStudent(id, updates) {
    const data = this.load();
    const idx = data.students.findIndex(s => s.id === id);
    if (idx === -1) return null;

    const old = data.students[idx];
    const merged = { ...old, ...updates };

    // 如果总金额或总课时变了，重新计算
    if (updates.totalAmount !== undefined || updates.totalHours !== undefined) {
      merged.totalAmount = +(merged.totalAmount || 0);
      merged.totalHours = +(merged.totalHours || 0);
      merged.perClassFee = merged.totalHours > 0
        ? +(merged.totalAmount / merged.totalHours).toFixed(2)
        : 0;
      // 重新计算已收和剩余
      merged.consumedAmount = +(merged.consumedHours * merged.perClassFee).toFixed(2);
      merged.receivedAmount = +(merged.totalAmount - merged.consumedAmount).toFixed(2);
      merged.remainingHours = +(merged.totalHours - merged.consumedHours).toFixed(2);
    }

    data.students[idx] = merged;
    this.save(data);
    return merged;
  },

  /**
   * 删除学员（同时删除其消课记录）
   */
  deleteStudent(id) {
    const data = this.load();
    data.students = data.students.filter(s => s.id !== id);
    data.records = data.records.filter(r => r.studentId !== id);
    this.save(data);
  },

  // ========== 消课记录相关 ==========

  /**
   * 获取所有消课记录
   */
  getRecords() {
    const data = this.load();
    return data ? data.records : [];
  },

  /**
   * 获取某学员的消课记录
   */
  getRecordsByStudent(studentId) {
    return this.getRecords().filter(r => r.studentId === studentId);
  },

  /**
   * 获取某日期的消课记录
   */
  getRecordsByDate(date) {
    return this.getRecords().filter(r => r.date === date);
  },

  /**
   * 批量消课
   * @param {Array} consumptions - [{ studentId, hours, date, note }]
   */
  addRecords(consumptions) {
    const data = this.load();
    const results = [];

    consumptions.forEach(item => {
      const student = data.students.find(s => s.id === item.studentId);
      if (!student) return;

      const hours = +item.hours;
      const amount = +(hours * student.perClassFee).toFixed(2);

      // 创建消课记录
      const record = {
        id: 'r_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
        studentId: student.id,
        studentName: student.name,
        date: item.date,
        hours: hours,
        amount: amount,
        perClassFee: student.perClassFee,
        note: item.note || ''
      };

      data.records.push(record);

      // 更新学员数据
      student.consumedHours = +(student.consumedHours + hours).toFixed(2);
      student.remainingHours = +(student.remainingHours - hours).toFixed(2);
      student.consumedAmount = +(student.consumedAmount + amount).toFixed(2);
      student.receivedAmount = +(student.receivedAmount - amount).toFixed(2);

      results.push(record);
    });

    this.save(data);
    return results;
  },

  /**
   * 删除消课记录（回退学员数据）
   */
  deleteRecord(recordId) {
    const data = this.load();
    const record = data.records.find(r => r.id === recordId);
    if (!record) return;

    // 回退学员数据
    const student = data.students.find(s => s.id === record.studentId);
    if (student) {
      student.consumedHours = +(student.consumedHours - record.hours).toFixed(2);
      student.remainingHours = +(student.remainingHours + record.hours).toFixed(2);
      student.consumedAmount = +(student.consumedAmount - record.amount).toFixed(2);
      student.receivedAmount = +(student.receivedAmount + record.amount).toFixed(2);
    }

    data.records = data.records.filter(r => r.id !== recordId);
    this.save(data);
  },

  // ========== 统计相关 ==========

  /**
   * 获取全局汇总数据
   */
  getSummary() {
    const data = this.load();
    const students = data.students;
    const records = data.records;

    return {
      totalStudents: students.length,
      totalReceived: +students.reduce((sum, s) => sum + s.receivedAmount, 0).toFixed(2),
      totalConsumed: +students.reduce((sum, s) => sum + s.consumedAmount, 0).toFixed(2),
      totalRemainingHours: +students.reduce((sum, s) => sum + s.remainingHours, 0).toFixed(2),
      totalConsumedHours: +students.reduce((sum, s) => sum + s.consumedHours, 0).toFixed(2),
      totalRecords: records.length
    };
  },

  /**
   * 按日期范围获取统计
   */
  getStatsByDateRange(startDate, endDate) {
    const records = this.getRecords().filter(r => {
      return r.date >= startDate && r.date <= endDate;
    });

    const byDate = {};
    const byStudent = {};

    records.forEach(r => {
      // 按日期汇总
      if (!byDate[r.date]) {
        byDate[r.date] = { date: r.date, hours: 0, amount: 0, count: 0 };
      }
      byDate[r.date].hours += r.hours;
      byDate[r.date].amount += r.amount;
      byDate[r.date].count += 1;

      // 按学员汇总
      if (!byStudent[r.studentId]) {
        byStudent[r.studentId] = {
          studentId: r.studentId,
          studentName: r.studentName,
          hours: 0,
          amount: 0,
          count: 0
        };
      }
      byStudent[r.studentId].hours += r.hours;
      byStudent[r.studentId].amount += r.amount;
      byStudent[r.studentId].count += 1;
    });

    return {
      records: records.sort((a, b) => b.date.localeCompare(a.date)),
      byDate: Object.values(byDate).sort((a, b) => b.date.localeCompare(a.date)),
      byStudent: Object.values(byStudent).sort((a, b) => b.hours - a.hours),
      totalHours: +records.reduce((s, r) => s + r.hours, 0).toFixed(2),
      totalAmount: +records.reduce((s, r) => s + r.amount, 0).toFixed(2),
      totalCount: records.length
    };
  }
};

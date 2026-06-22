// ============================================
// Charts - ECharts 图表配置
// 统一图表主题与初始化函数
// ============================================

const Charts = {
  // ---- 图表主题色 ----
  colors: ['#6366f1', '#3b82f6', '#22c55e', '#f97316', '#ec4899', '#06b6d4', '#8b5cf6', '#14b8a6'],

  // ---- 公共 tooltip ----
  _tooltip(extra) {
    return Object.assign({
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#1a1a2e', fontSize: 13 },
      padding: [10, 14]
    }, extra || {});
  },

  // ---- 公共 grid ----
  _grid(extra) {
    return Object.assign({ top: 40, right: 20, bottom: 30, left: 50, containLabel: true }, extra || {});
  },

  // =====================================================
  //  仪表盘 - 提问趋势折线图
  // =====================================================
  dashTrend(dom, data) {
    const chart = echarts.init(dom);
    chart.setOption({
      tooltip: this._tooltip(),
      grid: this._grid(),
      xAxis: {
        type: 'category',
        data: data.labels,
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 11 }
      },
      series: [{
        type: 'line',
        data: data.values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#6366f1', width: 3 },
        itemStyle: { color: '#6366f1', borderWidth: 2, borderColor: '#fff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99,102,241,0.25)' },
            { offset: 1, color: 'rgba(99,102,241,0.02)' }
          ])
        }
      }]
    });
    return chart;
  },

  // =====================================================
  //  仪表盘 - 课程分布饼图
  // =====================================================
  dashPie(dom, data) {
    const chart = echarts.init(dom);
    const pieData = [
      { value: data.machine_learning, name: '机器学习' },
      { value: data.data_mining, name: '数据挖掘' }
    ];
    chart.setOption({
      tooltip: this._tooltip({ trigger: 'item' }),
      legend: {
        bottom: 10,
        textStyle: { color: '#64748b', fontSize: 12 },
        itemWidth: 12, itemHeight: 12, itemGap: 20
      },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 12,
          color: '#64748b'
        },
        labelLine: { length: 15, length2: 8 },
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        data: pieData,
        color: ['#6366f1', '#3b82f6']
      }]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 提问趋势(双线: 机器学习 + 数据挖掘)
  // =====================================================
  analysisTrend(dom, data) {
    const chart = echarts.init(dom);
    chart.setOption({
      tooltip: this._tooltip({ trigger: 'axis' }),
      legend: {
        data: ['机器学习', '数据挖掘'],
        top: 5, right: 10,
        textStyle: { color: '#64748b', fontSize: 12 },
        itemWidth: 16, itemHeight: 3
      },
      grid: this._grid({ top: 50 }),
      xAxis: {
        type: 'category',
        data: data.labels,
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11, rotate: 30 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 11 }
      },
      series: [
        {
          name: '机器学习',
          type: 'line',
          data: data.ml,
          smooth: true,
          symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#6366f1', width: 2.5 },
          itemStyle: { color: '#6366f1' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(99,102,241,0.15)' },
              { offset: 1, color: 'rgba(99,102,241,0.01)' }
            ])
          }
        },
        {
          name: '数据挖掘',
          type: 'line',
          data: data.dm,
          smooth: true,
          symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#3b82f6', width: 2.5 },
          itemStyle: { color: '#3b82f6' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59,130,246,0.15)' },
              { offset: 1, color: 'rgba(59,130,246,0.01)' }
            ])
          }
        }
      ]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 知识点热度热力图
  // =====================================================
  topicHeatmap(dom, data) {
    const chart = echarts.init(dom);
    const heatData = [];
    data.matrix.forEach(function(row, ci) {
      row.forEach(function(val, ti) {
        heatData.push([ti, ci, val]);
      });
    });
    chart.setOption({
      tooltip: this._tooltip({
        trigger: 'item',
        formatter: function(p) {
          return data.topics[p.data[0]] + '<br>' + data.courses[p.data[1]] + '：' + p.data[2] + ' 次提问';
        }
      }),
      grid: this._grid({ left: 100, bottom: 60 }),
      xAxis: {
        type: 'category',
        data: data.topics,
        axisLabel: { color: '#64748b', fontSize: 11, rotate: 30 },
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisTick: { show: false },
        splitArea: { show: true, areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.04)'] } }
      },
      yAxis: {
        type: 'category',
        data: data.courses,
        axisLabel: { color: '#64748b', fontSize: 12 },
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisTick: { show: false }
      },
      visualMap: {
        min: 0, max: 30,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 5,
        inRange: {
          color: ['#e0e7ff', '#818cf8', '#6366f1', '#4f46e5', '#3730a3']
        },
        textStyle: { color: '#64748b' }
      },
      series: [{
        type: 'heatmap',
        data: heatData,
        label: { show: true, color: '#fff', fontSize: 13, fontWeight: 600 },
        itemStyle: { borderColor: '#fff', borderWidth: 3, borderRadius: 4 },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(99,102,241,0.4)' }
        }
      }]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 用户活跃(每日柱状图)
  // =====================================================
  userActivityBar(dom, data) {
    const chart = echarts.init(dom);
    chart.setOption({
      tooltip: this._tooltip({ trigger: 'axis' }),
      grid: this._grid(),
      xAxis: {
        type: 'category',
        data: data.daily.map(function(d) { return d.date; }),
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 11 }
      },
      series: [{
        type: 'bar',
        data: data.daily.map(function(d) { return d.count; }),
        barWidth: '45%',
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#818cf8' },
            { offset: 1, color: '#6366f1' }
          ])
        }
      }]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 活跃时段分布(柱状图)
  // =====================================================
  hourlyActivity(dom, data) {
    const chart = echarts.init(dom);
    chart.setOption({
      tooltip: this._tooltip({ trigger: 'axis' }),
      grid: this._grid(),
      xAxis: {
        type: 'category',
        data: data.hourly.map(function(d) { return d.hour + ':00'; }),
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 11 }
      },
      series: [{
        type: 'bar',
        data: data.hourly.map(function(d) { return d.count; }),
        barWidth: '55%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: function(params) {
            var v = params.data;
            return v >= 20 ? '#6366f1' : v >= 12 ? '#818cf8' : '#c7d2fe';
          }
        }
      }]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 满意度分布(环形图)
  // =====================================================
  satisfaction(dom, data) {
    const chart = echarts.init(dom);
    var total = data.total;
    var dist = data.distribution;
    var pieData = [
      { value: dist[5], name: '5星' },
      { value: dist[4], name: '4星' },
      { value: dist[3], name: '3星' },
      { value: dist[2], name: '2星' },
      { value: dist[1], name: '1星' }
    ];
    var satColors = ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff'];
    chart.setOption({
      tooltip: this._tooltip({
        trigger: 'item',
        formatter: '{b}: {c} 次 ({d}%)'
      }),
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        textStyle: { color: '#64748b', fontSize: 12 },
        itemWidth: 12, itemHeight: 12
      },
      series: [{
        type: 'pie',
        radius: ['50%', '75%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: function() { return ''; },
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 22,
            fontWeight: 700,
            formatter: function(p) { return p.data.name + '\n' + p.percent.toFixed(1) + '%'; }
          }
        },
        labelLine: { show: false },
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        data: pieData,
        color: satColors
      }],
      graphic: [{
        type: 'text',
        left: '36%',
        top: '44%',
        style: {
          text: data.avg.toFixed(1),
          textAlign: 'center',
          fill: '#1a1a2e',
          fontSize: 28,
          fontWeight: 700
        }
      }, {
        type: 'text',
        left: '36%',
        top: '56%',
        style: {
          text: '平均评分',
          textAlign: 'center',
          fill: '#94a3b8',
          fontSize: 12
        }
      }]
    });
    return chart;
  },

  // =====================================================
  //  数据分析 - 知识掌握度雷达图
  // =====================================================
  masteryRadar(dom, data) {
    var chart = echarts.init(dom);
    chart.setOption({
      tooltip: this._tooltip({ trigger: 'item' }),
      radar: {
        indicator: data.indicators.map(function(name) {
          return { name: name, max: 1 };
        }),
        radius: '65%',
        axisName: { color: '#64748b', fontSize: 12 },
        splitArea: {
          areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.04)', 'rgba(99,102,241,0.06)', 'rgba(99,102,241,0.08)', 'rgba(99,102,241,0.10)'] }
        },
        splitLine: { lineStyle: { color: '#e2e8f0' } },
        axisLine: { lineStyle: { color: '#e2e8f0' } }
      },
      series: [{
        type: 'radar',
        data: [{
          value: data.values,
          name: '掌握度',
          symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#6366f1', width: 2 },
          itemStyle: { color: '#6366f1' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(99,102,241,0.35)' },
              { offset: 1, color: 'rgba(99,102,241,0.05)' }
            ])
          }
        }]
      }]
    });
    return chart;
  },

  // =====================================================
  //  知识图谱 - ECharts 力导向图
  // =====================================================
  knowledgeGraph(dom, data, onNodeClick) {
    var chart = echarts.init(dom);
    var categories = data.categories.map(function(c) { return { name: c.name }; });
    var nodes = data.nodes.map(function(n) {
      var cat = data.categories[n.category];
      return {
        id: n.id,
        name: n.name,
        category: n.category,
        symbolSize: n.symbolSize || 30,
        itemStyle: { color: cat ? cat.color : '#6366f1' },
        label: { show: n.symbolSize >= 30, fontSize: 11, color: '#1a1a2e' }
      };
    });
    var relationColors = {
      'CONTAINS': '#6366f1',
      'BELONGS_TO': '#3b82f6',
      'EXTENDS': '#22c55e',
      'BASED_ON': '#22c55e',
      'USES': '#f97316',
      'APPLIES_TO': '#ec4899',
      'PREREQ': '#8b5cf6',
      'RELATED_TO': '#94a3b8',
      'EXPLAINS': '#94a3b8'
    };
    var edges = data.edges.map(function(e) {
      return {
        source: e.source,
        target: e.target,
        label: {
          show: true,
          formatter: e.relation,
          fontSize: 10,
          color: '#94a3b8'
        },
        lineStyle: {
          color: relationColors[e.relation] || '#c7d2fe',
          width: 1.5,
          curveness: 0.15
        }
      };
    });

    chart.setOption({
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#1a1a2e', fontSize: 13 },
        formatter: function(p) {
          if (p.dataType === 'node') {
            var cat = data.categories[p.data.category];
            return '<b>' + p.data.name + '</b><br/>类型：' + (cat ? cat.name : '未知');
          }
          return p.data.source + ' → ' + p.data.target;
        }
      },
      legend: {
        data: categories.map(function(c) { return c.name; }),
        top: 10,
        textStyle: { color: '#64748b', fontSize: 12 },
        itemWidth: 14, itemHeight: 14
      },
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: edges,
        categories: categories,
        roam: true,
        draggable: true,
        force: {
          repulsion: 280,
          gravity: 0.08,
          edgeLength: [80, 200],
          friction: 0.6
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 3 },
          label: { fontSize: 13, fontWeight: 700 }
        },
        label: { position: 'right' },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 8]
      }]
    });

    if (onNodeClick) {
      chart.on('click', function(params) {
        if (params.dataType === 'node') {
          onNodeClick(params.data);
        }
      });
    }
    return chart;
  },

  // ---- 窗口大小变化时自动调整图表 ----
  _instances: [],
  register(chart) { this._instances.push(chart); return chart; },
  resizeAll() { this._instances.forEach(function(c) { try { c.resize(); } catch (e) {} }); }
};

// 全局 resize 监听
window.addEventListener('resize', function() {
  if (window._chartResizeTimer) clearTimeout(window._chartResizeTimer);
  window._chartResizeTimer = setTimeout(function() {
    Charts.resizeAll();
  }, 200);
});

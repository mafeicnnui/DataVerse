<template>
  <div class="app-layout" :class="{ collapsed: sidebarCollapsed }" :style="layoutStyle" :data-theme="theme" ref="appLayoutRef">
    <!-- 左侧菜单区 -->
    <aside class="sidebar" ref="sidebarRef" :style="sidebarInlineStyle">
      <div class="brand" title="星辰疆域，数据宇宙">
        <img src="/dataverse_logo.png" alt="DataVerse" class="brand-logo" />
        <span class="brand-name">辰域运维平台</span>
      </div>
      <nav>
        <ul>
          <li :class="{active: activeTab==='conn'}" @click="openTab('conn','连接管理')">
            <span class="mi" aria-hidden="true">
              <!-- 更清晰的链路图标，尺寸 20px -->
              <svg viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px">
                <path d="M8.5 13.5a3 3 0 0 1 0-4.24l3-3a3 3 0 0 1 4.24 4.24l-.88.88-1.41-1.41.88-.88a1 1 0 0 0-1.41-1.41l-3 3a1 1 0 1 0 1.41 1.41l.29-.29 1.41 1.41-.29.29a3 3 0 0 1-4.24 0Zm7 7a3 3 0 0 1-4.24 0l-1.17-1.17 1.41-1.41 1.17 1.17a1 1 0 0 0 1.41-1.41l-3-3a1 1 0 1 0-1.41 1.41l.88.88-1.41 1.41-.88-.88a3 3 0 0 1 4.24-4.24l3 3a3 3 0 0 1 0 4.24Z"/>
              </svg>
            </span>
            <span>连接管理</span>
          </li>
          <li :class="{active: activeTab==='server'}" @click="openTab('server','主机管理')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 6c0-1.1.9-2 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6zm0 8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2zm3-7h2v2H7V7zm0 8h2v2H7v-2z"/></svg>
            </span>
            <span>主机管理</span>
          </li>
          <!-- 工单平台（含二级菜单） -->
          <li class="group">
            <div class="group-title" @click="dataMenuOpen = !dataMenuOpen" :aria-expanded="dataMenuOpen" title="工单平台">
              <span class="mi-wrap">
                <span class="mi" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14l4-4h12c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
                </span>
                <span>工单平台</span>
              </span>
              <span class="arrow" :class="{ open: dataMenuOpen }">›</span>
            </div>
            <ul v-show="dataMenuOpen" class="sub">
              <li :class="{active: activeTab==='ticket.query'}" @click="openTab('ticket.query','工单查询')">工单查询</li>
              <li :class="{active: activeTab==='ticket.publish'}" @click="openTab('ticket.publish','工单发布')">工单发布</li>
              <li :class="{active: activeTab==='ticket.review'}" @click="openTab('ticket.review','工单审核')">工单审核</li>
              <li :class="{active: activeTab==='ticket.run'}" @click="openTab('ticket.run','工单运行')">工单运行</li>
            </ul>
          </li>
          <li :class="{active: activeTab==='report.platform'}" @click="openTab('report.platform','报表平台')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg>
            </span>
            <span>报表平台</span>
          </li>
          <li :class="{active: activeTab==='screen.mgmt'}" @click="openTab('screen.mgmt','大屏管理')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 3H3c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h7v2H8v2h8v-2h-2v-2h7c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
            </span>
            <span>大屏管理</span>
          </li>
          <li :class="{active: activeTab==='report.task'}" @click="openTab('report.task','报表任务')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14l4-4h12c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4 9H7v-2h8v2zm2-4H7V6h10v2z"/></svg>
            </span>
            <span>报表任务</span>
          </li>
          <li :class="{active: activeTab==='user.mgmt'}" @click="openTab('user.mgmt','用户管理')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"/></svg>
            </span>
            <span>用户管理</span>
          </li>
          <li :class="{active: activeTab==='role.mgmt'}" @click="openTab('role.mgmt','角色管理')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.7 0 3-1.3 3-3s-1.3-3-3-3-3 1.3-3 3 1.3 3 3 3zm-8 0c1.7 0 3-1.3 3-3S9.7 5 8 5 5 6.3 5 8s1.3 3 3 3zm0 2c-2.7 0-8 1.3-8 4v3h10v-2c0-1.2.5-2.3 1.3-3.2-1.1-.5-2.4-.8-3.3-.8zm8 0c-.9 0-2.2.3-3.3.8.8.9 1.3 2 1.3 3.2v2h10v-3c0-2.7-5.3-4-8-4z"/></svg>
            </span>
            <span>角色管理</span>
          </li>
          <li :class="{active: activeTab==='sys.settings'}" @click="openTab('sys.settings','系统设置')">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.31.06-.63.06-.94s-.02-.63-.06-.94l2.03-1.58a.5.5 0 0 0 .12-.64l-1.92-3.32a.5.5 0 0 0-.6-.22l-2.39.96a7.03 7.03 0 0 0-1.63-.94l-.36-2.54A.5.5 0 0 0 14.3 1h-4.6a.5.5 0 0 0-.49.41l-.36 2.54c-.58.22-1.12.52-1.63.94L4.83 4.47a.5.5 0 0 0-.6.22L2.31 7.99a.5.5 0 0 0 .12.64l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94L2.43 15.67a.5.5 0 0 0-.12.64l1.92 3.32c.14.24.43.34.69.22l2.39-.96c.51.42 1.05.72 1.63.94l.36 2.54c.05.24.25.41.49.41h4.6c.24 0 .44-.17.49-.41l.36-2.54c.58-.22 1.12-.52 1.63-.94l2.39.96c.26.11.55.01.69-.22l1.92-3.32a.5.5 0 0 0-.12-.64l-2.03-1.58zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5S10.07 8.5 12 8.5s3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/></svg>
            </span>
            <span>系统设置</span>
          </li>
        </ul>
      </nav>
    </aside>
    <!-- 侧栏右侧拖拽条（替代折叠按钮） -->
    <div class="sidebar-resizer" @mousedown="startResizeSidebar" title="拖动调整侧栏宽度"></div>

    <!-- 右侧预览区 -->
    <main class="preview" ref="previewRef" :style="`padding-left:${contentPad}px !important; padding-right:${contentPad}px !important;`">
      <!-- 顶部信息栏：时间/农历 | 天气/建议 | 头像 -->
      <header class="top-info">
        <div class="info-left">
          <div class="datetime">{{ dateTimeText }} <span v-if="lunarText">{{ lunarText }}</span></div>
        </div>
        <div class="info-center">
          <div class="weather" v-if="weatherText">{{ weatherText }}</div>
          <div class="advice" v-if="adviceText">{{ adviceText }}</div>
        </div>
        <div class="info-right">
          <select class="theme-select" v-model="theme" title="主题">
            <option value="lightBlue">浅蓝</option>
            <option value="grayBlue">灰蓝</option>
            <option value="mint">淡紫</option>
            <option value="pure">纯色</option>
          </select>
          <img class="avatar" src="https://cdn.jsdelivr.net/npm/twemoji@14.0.2/assets/72x72/1f431.png" alt="" loading="lazy" decoding="async" @error="onAvatarError" />
        </div>
      </header>

      <!-- 标签栏：还原为修改前的简单样式 -->
      <div class="tabs-bar">
        <div v-for="t in tabs" :key="t.key" class="tab-item" :class="{active: t.key===activeTab}" @click="switchTab(t.key)">
          <span class="tab-title">{{ t.title }}</span>
          <span class="tab-close" title="关闭" @click.stop="closeTab(t.key)">×</span>
        </div>
      </div>
      <div v-if="activeTab==='conn'" class="container">
        <ConnManager />
      </div>
      <div v-else-if="activeTab==='server'" class="container">
        <HostManager />
      </div>

      <div v-else-if="activeTab==='ticket.query'" class="container ticket-query" ref="tqContainerRef">
        <h1 class="section-title">工单查询</h1>

        <!-- 顶部工具栏：数据源/数据库/过滤 + 操作按钮 -->
        <div class="card section-block tq-toolbar">
          <div class="tq-toolbar-row">
            <label class="icon-label tq-conn" aria-label="连接">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.9 12a5 5 0 0 1 5-5h3v2h-3a3 3 0 1 0 0 6h3v2h-3a5 5 0 0 1-5-5Zm7.2 1h1.8v-2h-1.8v2Zm3-6h3a5 5 0 1 1 0 10h-3v-2h3a3 3 0 1 0 0-6h-3V7Z"/></svg></span>
              <select v-model.number="tq.selectedConnId" @change="onConnChange">
                <option value="">请选择连接</option>
                <option v-for="c in tq.conns" :key="c.id" :value="c.id">
                  {{ c.description || (c.ip + ':' + c.port) || ('#' + c.id) }}
                </option>
              </select>
            </label>
            <label class="icon-label" aria-label="数据库">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-4.97 0-9 1.79-9 4v10c0 2.21 4.03 4 9 4s9-1.79 9-4V7c0-2.21-4.03-4-9-4Zm0 2c3.87 0 7 .9 7 2s-3.13 2-7 2-7-.9-7-2 3.13-2 7-2Zm0 14c-3.86 0-7-1.01-7-2.25V14c1.73 1.05 4.54 1.75 7 1.75s5.27-.7 7-1.75v2.75C19 17.99 15.86 19 12 19Zm0-5c-3.86 0-7-1.01-7-2.25V9c1.73 1.05 4.54 1.75 7 1.75S17.27 10.05 19 9v2.75C19 12.99 15.86 14 12 14Z"/></svg></span>
              <div class="tq-db-multi" ref="tqDbMultiRef" :class="{ disabled: !tq.selectedConnId }">
                <div class="tq-db-summary" :title="tq.selectedDbs.length ? tq.selectedDbs.join(', ') : '请选择数据库'" @click="toggleDbDropdown" :aria-expanded="tq.dbDropdownOpen">
                  <span class="placeholder" v-if="!tq.selectedDbs.length">请选择数据库</span>
                  <template v-else>
                    <span class="tag">{{ tq.selectedDbs[0] }}</span>
                    <span v-if="tq.selectedDbs.length>1" class="more">+{{ tq.selectedDbs.length-1 }}</span>
                  </template>
                  <span class="caret">▾</span>
                </div>
                <!-- 全屏透明遮罩：用于点击外部关闭下拉 -->
                <div v-if="tq.dbDropdownOpen" class="tq-db-overlay" @mousedown="tq.dbDropdownOpen=false" aria-hidden="true"></div>
                <div v-if="tq.dbDropdownOpen" class="tq-db-panel"
                     @mousedown.stop @mouseup.stop
                     @pointerdown.stop @pointerup.stop @pointermove.stop
                     @wheel.stop
                     @click.stop @mousemove.stop
                     @mouseenter="tq.dbPanelHover=true" @mouseleave="tq.dbPanelHover=false"
                     @scroll.capture.stop>
                  <div class="tq-db-search-wrap">
                    <input class="tq-db-search" ref="tqDbSearchRef" v-model="tq.dbSearch" placeholder="搜索数据库..." @wheel.stop @mousedown.stop @mouseup.stop @click.stop />
                    <button type="button" class="tq-db-clear" title="清空选择" @click.stop="clearDbSelection" aria-label="清空选择" role="button">×</button>
                  </div>
                  <div class="tq-db-list" ref="tqDbListRef"
                       @mousedown.stop @mouseup.stop
                       @pointerdown.stop @pointerup.stop @pointermove.stop
                       @wheel.stop
                       @click.stop @mousemove.stop
                       @scroll.capture.stop>
                    <label v-for="db in filteredDatabases" :key="'opt-'+db" class="opt" @wheel.stop @mousedown.stop @mouseup.stop @click.stop>
                      <input type="checkbox" :value="db" :checked="tq.selectedDbs.includes(db)" @change="onDbToggle(db, $event)" @wheel.stop @mousedown.stop @mouseup.stop @click.stop />
                      <span class="txt">{{ db }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </label>
            <label class="icon-label tq-filter" aria-label="过滤">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 5h18v2l-7 7v4l-4 2v-7L3 5Z"/></svg></span>
              <input v-model="tq.filter" placeholder="过滤表名，支持模糊匹配" />
            </label>
            <div class="tq-actions" style="margin-left:auto;">
              <button class="icon-btn add" title="执行 (Ctrl+Enter)" @click="executeSQL" :disabled="tq.running || !tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              </button>
              <button class="icon-btn warn" title="停止" @click="stopExecution" :disabled="!tq.running">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
              </button>
              <button class="icon-btn info" title="美化SQL" @click="beautifySQL" :disabled="!tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/></svg>
              </button>
              <button class="icon-btn" title="查看执行计划" @click="viewPlan" :disabled="!tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg>
              </button>
              <button class="icon-btn" title="导出 CSV" @click="exportCSV" :disabled="!(tq.result && tq.result.type==='table')">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7H3l9-9 9 9h-2Zm-7 7h2v-6h-2v6Z"/></svg>
              </button>
              <button class="icon-btn" title="导出 Excel" @click="exportExcel" :disabled="!(tq.result && tq.result.type==='table')">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h9a1 1 0 0 1 1 1v3h6v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Zm9 5V6H5v12h14V9h-6Zm-6.5 7 2.75-4L6.5 8h2.3l1.55 2.6L11.9 8h2.3l-2.75 4 2.75 4h-2.3l-1.55-2.6L8.8 16H6.5Z"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 下方面板：左树右编辑器+结果 -->
        <div class="card section-block tq-main" ref="tqMainRef" :class="{ 'collapsed-left': tq.leftCollapsed }" :style="{ gridTemplateColumns: tq.leftCollapsed ? '0 1fr' : '230px 1fr' }">
          <div class="tq-left" @mousedown="(tq.dbDropdownOpen=false, !(tq.selectedDbs && tq.selectedDbs.length>=1) && (tq.forceTreeFilter=false))">
              <div class="tq-tree" role="tree">
              <div class="tq-tree-db" v-for="db in tq.databases" :key="db" v-show="(!tq.filter || db.includes(tq.filter)) && (!(tq.forceTreeFilter && tq.selectedDbs && tq.selectedDbs.length>=1) || tq.selectedDbs.includes(db))">
                <div class="tq-tree-db-name" @click="(tq.dbDropdownOpen=false, !(tq.selectedDbs && tq.selectedDbs.length>=1) && (tq.forceTreeFilter=false), toggleDbExpand(db))">
                  <span class="arrow" :class="{open: tq.expandedDb[db]}" aria-hidden="true">›</span>
                  <span>{{ db }}</span>
                  <!-- 悬停显示的过滤按钮；有过滤条件时常显并高亮 -->
                  <button
                    class="tq-db-filter-btn"
                    :class="{ active: !!(tq.tableFilters && tq.tableFilters[db]) }"
                    title="过滤当前库的表"
                    @click.stop="tq.tableFilterOpenFor = (tq.tableFilterOpenFor===db ? '' : db)"
                    aria-label="过滤当前库的表"
                  >
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M3 5h18l-7 8v5l-4 2v-7L3 5z"/></svg>
                  </button>
                </div>
                <!-- 浮动过滤框：点击过滤图标后打开；录入完成/失焦后自动隐藏 -->
                <div v-if="tq.tableFilterOpenFor===db" class="tq-table-filter-pop" @mousedown.stop>
                  <input
                    class="tq-table-filter"
                    v-model="tq.tableFilters[db]"
                    placeholder="过滤当前库的表..."
                    autofocus
                    @keydown.esc.prevent="tq.tableFilterOpenFor=''"
                    @keydown.enter.prevent="tq.expandedDb[db]=true; tq.tableFilterOpenFor=''"
                    @blur="tq.expandedDb[db]=true; tq.tableFilterOpenFor=''"
                  />
                  <button
                    v-if="tq.tableFilters[db]"
                    class="tq-table-filter-clear"
                    @click.stop="tq.tableFilters[db]=''; tq.tableFilterOpenFor=''"
                    title="清空"
                    aria-label="清空"
                  >×</button>
                </div>
                <ul v-show="tq.expandedDb[db]" class="tq-tree-tables">
                  <li v-for="tbl in filteredTables(db)" :key="db + ':' + tbl" @click="appendTableToSQL(db, tbl)">
                    {{ tbl }}
                  </li>
                  <li v-if="tq.tablesLoading[db]" class="muted">加载中...</li>
                  <li v-if="!tq.tablesLoading[db] && (!tq.tables[db] || tq.tables[db].length===0)" class="muted">无表</li>
                </ul>
              </div>
              </div>
          </div>
          <button v-if="tq.selectedConnId && tq.databases && tq.databases.length" class="tq-left-toggle" :class="{ collapsed: tq.leftCollapsed }" @click="tq.leftCollapsed = !tq.leftCollapsed" :title="tq.leftCollapsed ? '展开连接菜单' : '隐藏连接菜单'" aria-label="切换左侧菜单">
            <span class="chev" aria-hidden="true">{{ tq.leftCollapsed ? '›' : '‹' }}</span>
          </button>
          <div class="tq-right" ref="tqRightRef">
            <!-- 紧凑型标签栏 -->
            <SqlTabs />
            <div class="tq-editor-host" :style="{ height: Math.max(0, Number(tq.editorHeight||0)) + 'px' }" @click="onSqlHostClick">
              <SqlEditor />
            </div>
            <div class="tq-vsplit" title="拖动调整编辑器与结果高度" @mousedown="startEditorVResize"></div>
            <div class="tq-result">
              <div class="tq-result-body">
                <template v-if="tq.result && tq.result.type==='table'">
                  <ResultTable />
                </template>
                <template v-else-if="tq.result && tq.result.type==='text'">
                  <pre class="tq-text">{{ tq.result.text }}</pre>
                </template>
                <template v-else>
                  <div class="muted">在此显示查询结果或执行信息</div>
                </template>
              </div>
              <!-- 分页：放在结果体下面，属于卡片内的底部工具区 -->
              <div v-if="tq.result && tq.result.type==='table'" class="tq-pagination">
                <button class="icon-btn" @click="goToPage(tq.page - 1)" :disabled="tq.page <= 1" title="上一页">‹</button>
                <span class="muted">第 {{ tq.page }} / {{ tqTotalPages }} 页</span>
                <input
                  class="page-input"
                  type="number"
                  min="1"
                  :max="tqTotalPages"
                  v-model.number="tq.pageInput"
                  @keydown.enter.prevent="goToPage(tq.pageInput)"
                  :placeholder="`跳转页 (1-${tqTotalPages})`"
                  style="width:84px;margin:0 6px;padding:4px 6px;border:1px solid #c7d2fe;border-radius:6px;"
                  title="输入页码后按回车跳转"
                />
                <button class="icon-btn" @click="goToPage(tq.page + 1)" :disabled="tq.page >= tqTotalPages" title="下一页">›</button>
                <span class="muted" style="margin-left:8px;">每页</span>
                <select v-model.number="tq.pageSize" @change="goToPage(1)">
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <span class="muted">条，共 {{ tq.totalRows || 0 }} 条</span>
                <span v-if="tq.result && tq.result.rows && tq.result.rows.length" class="muted" style="margin-left:12px;">
                  首行ID：{{ (() => { try { const cols = tq.result.columns||[]; const idKey = cols.includes('id') ? 'id' : cols[0]; return tq.result.rows[0]?.[idKey] ?? tq.result.rows[0]?.[0] } catch { return '' } })() }}
                </span>
              </div>
            </div>
          </div>
          <!-- 右上角通知 -->
          <div class="tq-notices">
            <div class="tq-notice" v-for="n in tq.notices" :key="n.id">{{ n.text }}</div>
          </div>
        </div>
      </div>
      <div v-else class="container">
        <h1>{{ activeTitle }}</h1>
        <p>该功能即将上线，敬请期待。</p>
      </div>
    </main>
    <!-- 控制台模态窗口：复用工单查询能力，固定为指定连接，数据库菜单为该连接下的库 -->
    <div v-if="consoleModal.open" class="dv-modal" role="dialog" aria-modal="true">
      <div class="dv-modal-backdrop" aria-hidden="true"></div>
      <div class="dv-modal-panel ticket-query" role="document">
        <header class="dv-modal-header">
          <h2 class="section-title">控制台 <span class="console-conn-info" v-if="consoleConnInfo">[{{ consoleConnInfo }}]</span></h2>
          <!-- 顶部右侧返回按钮（倒弯箭头） -->
          <button class="modal-back-btn" title="返回" aria-label="返回" @click="closeConsole">↩</button>
        </header>
        <div class="card section-block tq-toolbar">
          <div class="tq-toolbar-row">
            <!-- 连接显示为只读（固定为当前选择） -->
            <label class="icon-label tq-conn" aria-label="连接">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.9 12a5 5 0 0 1 5-5h3v2h-3a3 3 0 1 0 0 6h3v2h-3a5 5 0 0 1-5-5Zm7.2 1h1.8v-2h-1.8v2Zm3-6h3a5 5 0 1 1 0 10h-3v-2h3a3 3 0 1 0 0-3h-3v-2Z"/></svg></span>
              <div class="tq-conn-readonly" :title="consoleConnLabel">{{ consoleConnLabel }}</div>
            </label>
            <label class="icon-label" aria-label="数据库">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-4.97 0-9 1.79-9 4v10c0 2.21 4.03 4 9 4s9-1.79 9-4V7c0-2.21-4.03-4-9-4Zm0 2c3.87 0 7 .9 7 2s-3.13 2-7 2-7-.9-7-2 3.13-2 7-2Zm0 14c-3.86 0-7-1.01-7-2.25V14c1.73 1.05 4.54 1.75 7 1.75s5.27-.7 7-1.75v2.75C19 17.99 15.86 19 12 19Zm0-5c-3.86 0-7-1.01-7-2.25V9c1.73 1.05 4.54 1.75 7 1.75S17.27 10.05 19 9v2.75C19 12.99 15.86 14 12 14Z"/></svg></span>
              <!-- 复用多选下拉，受 tq.selectedConnId 限制（已固定） -->
              <div class="tq-db-multi" :class="{ disabled: !tq.selectedConnId }">
                <div class="tq-db-summary" :title="tq.selectedDbs.length ? tq.selectedDbs.join(', ') : '请选择数据库'" @click="toggleDbDropdown" :aria-expanded="tq.dbDropdownOpen">
                  <span class="placeholder" v-if="!tq.selectedDbs.length">请选择数据库</span>
                  <template v-else>
                    <span class="tag">{{ tq.selectedDbs[0] }}</span>
                    <span v-if="tq.selectedDbs.length>1" class="more">+{{ tq.selectedDbs.length-1 }}</span>
                  </template>
                  <span class="caret">▾</span>
                </div>
                <div v-if="tq.dbDropdownOpen" class="tq-db-overlay" @mousedown="tq.dbDropdownOpen=false" aria-hidden="true"></div>
                <div v-if="tq.dbDropdownOpen" class="tq-db-panel"
                     @mousedown.stop @mouseup.stop
                     @pointerdown.stop @pointerup.stop @pointermove.stop
                     @wheel.stop
                     @click.stop @mousemove.stop
                     @mouseenter="tq.dbPanelHover=true" @mouseleave="tq.dbPanelHover=false"
                     @scroll.capture.stop>
                  <div class="tq-db-search-wrap">
                    <input class="tq-db-search" v-model="tq.dbSearch" placeholder="搜索数据库..." @wheel.stop @mousedown.stop @mouseup.stop @click.stop />
                    <button type="button" class="tq-db-clear" title="清空选择" @click.stop="clearDbSelection" aria-label="清空选择" role="button">×</button>
                  </div>
                  <div class="tq-db-list"
                       @mousedown.stop @mouseup.stop
                       @pointerdown.stop @pointerup.stop @pointermove.stop
                       @wheel.stop
                       @click.stop @mousemove.stop
                       @scroll.capture.stop>
                    <label v-for="db in filteredDatabases" :key="'opt-m-'+db" class="opt" @wheel.stop @mousedown.stop @mouseup.stop @click.stop>
                      <input type="checkbox" :value="db" :checked="tq.selectedDbs.includes(db)" @change="onDbToggle(db, $event)" @wheel.stop @mousedown.stop @mouseup.stop @click.stop />
                      <span class="txt">{{ db }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </label>
            <label class="icon-label tq-filter" aria-label="过滤">
              <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 5h18v2l-7 7v4l-4 2v-7L3 5Z"/></svg></span>
              <input v-model="tq.filter" placeholder="过滤表名，支持模糊匹配" />
            </label>
            <div class="tq-actions">
              <button class="icon-btn add" title="执行 (Ctrl+Enter)" @click="executeSQL" :disabled="tq.running || !tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              </button>
              <button class="icon-btn warn" title="停止" @click="stopExecution" :disabled="!tq.running">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
              </button>
              <button class="icon-btn info" title="美化SQL" @click="beautifySQL" :disabled="!tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/></svg>
              </button>
              <button class="icon-btn" title="查看执行计划" @click="viewPlan" :disabled="!tq.sql.trim()">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg>
              </button>
              <button class="icon-btn" title="导出 CSV" @click="exportCSV" :disabled="!(tq.result && tq.result.type==='table')">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7H3l9-9 9 9h-2Zm-7 7h2v-6h-2v6Z"/></svg>
              </button>
              <button class="icon-btn" title="导出 Excel" @click="exportExcel" :disabled="!(tq.result && tq.result.type==='table')">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h9a1 1 0 0 1 1 1v3h6v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Zm9 5V6H5v12h14V9h-6Zm-6.5 7 2.75-4L6.5 8h2.3l1.55 2.6L11.9 8h2.3l-2.75 4 2.75 4h-2.3l-1.55-2.6L8.8 16H6.5Z"/></svg>
              </button>
            </div>
          </div>
        </div>
        <div class="card section-block tq-main" :class="{ 'collapsed-left': tq.leftCollapsed }" :style="{ gridTemplateColumns: tq.leftCollapsed ? '0 1fr' : '230px 1fr' }">
          <div class="tq-left">
            <div class="tq-tree" role="tree">
              <div class="tq-tree-db" v-for="db in tq.databases" :key="'mdb-'+db" v-show="(!tq.filter || db.includes(tq.filter)) && (!(tq.forceTreeFilter && tq.selectedDbs && tq.selectedDbs.length>=1) || tq.selectedDbs.includes(db))">
                <div class="tq-tree-db-name" @click="(tq.dbDropdownOpen=false, !(tq.selectedDbs && tq.selectedDbs.length>=1) && (tq.forceTreeFilter=false), toggleDbExpand(db))">
                  <span class="arrow" :class="{open: tq.expandedDb[db]}" aria-hidden="true">›</span>
                  <span>{{ db }}</span>
                </div>
                <ul v-show="tq.expandedDb[db]" class="tq-tree-tables">
                  <li v-for="tbl in filteredTables(db)" :key="'mt-'+db+'-'+tbl" @click="appendTableToSQL(db, tbl)">
                    {{ tbl }}
                  </li>
                  <li v-if="tq.tablesLoading[db]" class="muted">加载中...</li>
                  <li v-if="!tq.tablesLoading[db] && (!tq.tables[db] || tq.tables[db].length===0)" class="muted">无表</li>
                </ul>
              </div>
            </div>
          </div>
          <button
            v-if="tq.selectedConnId && tq.databases && tq.databases.length"
            class="tq-left-toggle"
            :class="{ collapsed: tq.leftCollapsed }"
            @click="tq.leftCollapsed = !tq.leftCollapsed"
            :title="tq.leftCollapsed ? '展开连接菜单' : '隐藏连接菜单'"
            aria-label="切换左侧菜单"
          >
            <span class="chev" aria-hidden="true">{{ tq.leftCollapsed ? '›' : '‹' }}</span>
          </button>
          <div class="tq-right" ref="tqRightRef">
            <SqlTabs />
            <div class="tq-editor-wrap" :style="{ height: Math.max(0, Number(tq.editorHeight||0)) + 'px' }">
              <SqlEditor />
            </div>
            <div class="tq-vsplit" @mousedown="startEditorVResize" title="拖动调整编辑器高度"></div>
            <div class="tq-result">
              <div class="tq-result-body">
                <template v-if="tq.result && tq.result.type==='table'">
                  <ResultTable />
                </template>
                <template v-else-if="tq.result && tq.result.type==='text'">
                  <pre class="tq-text">{{ tq.result.text }}</pre>
                </template>
                <template v-else>
                  <div class="muted">在此显示查询结果或执行信息</div>
                </template>
              </div>
              <div v-if="tq.result && tq.result.type==='table'" class="tq-pagination">
                <button class="icon-btn" @click="goToPage(tq.page - 1)" :disabled="tq.page <= 1" title="上一页">‹</button>
                <span class="muted">第 {{ tq.page }} / {{ tqTotalPages }} 页</span>
                <input
                  class="page-input"
                  type="number"
                  min="1"
                  :max="tqTotalPages"
                  v-model.number="tq.pageInput"
                  @keydown.enter.prevent="goToPage(tq.pageInput)"
                  :placeholder="`跳转页 (1-${tqTotalPages})`"
                  style="width:84px;margin:0 6px;padding:4px 6px;border:1px solid #c7d2fe;border-radius:6px;"
                  title="输入页码后按回车跳转"
                />
                <button class="icon-btn" @click="goToPage(tq.page + 1)" :disabled="tq.page >= tqTotalPages" title="下一页">›</button>
                <span class="muted" style="margin-left:8px;">每页</span>
                <select v-model.number="tq.pageSize" @change="goToPage(1)">
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <span class="muted">条，共 {{ tq.totalRows || 0 }} 条</span>
                <span v-if="tq.result && tq.result.rows && tq.result.rows.length" class="muted" style="margin-left:12px;">
                  首行ID：{{ (() => { try { const cols = tq.result.columns||[]; const idKey = cols.includes('id') ? 'id' : cols[0]; return tq.result.rows[0]?.[idKey] ?? tq.result.rows[0]?.[0] } catch { return '' } })() }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 全局提示（置顶，不被弹窗遮挡） -->
    <div class="global-notices" aria-live="polite" aria-atomic="false">
      <div v-for="n in globalNotices" :key="n.id" class="toast">{{ n.text }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed, nextTick, watch, onBeforeUnmount, provide } from 'vue'
import ResultTable from './components/ticket/ResultTable.vue'
import SqlTabs from './components/ticket/SqlTabs.vue'
import SqlEditor from './components/ticket/SqlEditor.vue'
import ConnManager from './components/conn/ConnManager.vue'
import HostManager from './components/server/HostManager.vue'
import api from './api'
// CodeMirror 6
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, highlightActiveLine } from '@codemirror/view'
import { autocompletion, CompletionContext } from '@codemirror/autocomplete'
import { sql, MySQL } from '@codemirror/lang-sql'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'

// ===== 主题切换（四套方案，仅作用于侧栏背景与分隔线） =====
const theme = ref('lightBlue')
const sidebarRef = ref(null)
const themePresets = {
  lightBlue: {
    '--sidebar-bg': 'linear-gradient(180deg, #e9f2ff 0%, #d9e8ff 100%)',
    '--sidebar-border': '#cfe0ff'
  },
  grayBlue: {
    '--sidebar-bg': 'linear-gradient(180deg, #f0f2f5 0%, #e3e7ee 100%)',
    '--sidebar-border': '#cfd5e1'
  },
  mint: {
    '--sidebar-bg': 'linear-gradient(180deg, #f4e9ff 0%, #ead8ff 100%)',
    '--sidebar-border': '#ddc8ff'
  },
  pure: {
    '--sidebar-bg': '#f7f7f7',
    '--sidebar-border': '#e1e1e1'
  }
}
function applyTheme(name) {
  const vars = themePresets[name] || themePresets.lightBlue
  const root = document.documentElement
  Object.entries(vars).forEach(([k, v]) => {
    try { root.style.setProperty(k, v) } catch {}
    try { sidebarRef.value && sidebarRef.value.style.setProperty(k, v) } catch {}
  })
  try { localStorage.setItem('dv-theme', name) } catch {}
}
onMounted(() => {
  try {
    const saved = localStorage.getItem('dv-theme')
    if (saved && themePresets[saved]) theme.value = saved
  } catch {}
  applyTheme(theme.value)
})
watch(() => theme.value, v => applyTheme(v))
const sidebarInlineStyle = computed(() => {
  const vars = themePresets[theme.value] || themePresets.lightBlue
  return { background: vars['--sidebar-bg'], borderRightColor: vars['--sidebar-border'] }
})

// ===== 侧栏宽度拖拽 =====
const contentPad = ref(16)
const appLayoutRef = ref(null)
const isResizingSidebar = ref(false)
function setSidebarW(px) {
  const min = 150, max = 360
  const n = Math.max(min, Math.min(max, Math.round(px)))
  try {
    const host = appLayoutRef.value || document.documentElement
    host.style.setProperty('--sidebar-w', n + 'px')
    // 直接同步 grid 模板，确保立即重排
    try { host.style.gridTemplateColumns = n + 'px 1fr' } catch {}
    // 同步侧栏节点自身宽度，避免子元素因最小宽度导致滞后
    try {
      if (sidebarRef.value) {
        sidebarRef.value.style.width = n + 'px'
        sidebarRef.value.style.minWidth = n + 'px'
        sidebarRef.value.style.maxWidth = n + 'px'
      }
    } catch {}
    localStorage.setItem('dv-sidebar-w', String(n))
  } catch {}
}
function startResizeSidebar(e) {
  try { e.preventDefault() } catch {}
  isResizingSidebar.value = true
  const rect = (appLayoutRef.value || document.body).getBoundingClientRect()
  const onMove = (ev) => {
    const x = ev.clientX - rect.left
    setSidebarW(x)
  }
  const onUp = () => {
    isResizingSidebar.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}
onMounted(() => {
  try { const saved = parseInt(localStorage.getItem('dv-sidebar-w') || '') ; if (!Number.isNaN(saved)) setSidebarW(saved) } catch {}
})

// --- 控制台模态：状态与方法（移入 <script setup>，使用纯 JS） ---
const consoleModal = reactive({ open: false, connId: null })
const consoleConnLabel = computed(() => {
  try {
    const arr = (tq && tq.conns) ? tq.conns : []
    const c = (arr || []).find((x) => x.id === consoleModal.connId)
    if (!c) return `#${consoleModal.connId ?? ''}`
    return c.description || `${c.ip}:${c.port}` || `#${c.id}`
  } catch { return `#${consoleModal.connId ?? ''}` }
})

// 控制台标题后显示的简短连接信息 [user@IP:port\\db]
const consoleConnInfo = computed(() => {
  try {
    const arr = (tq && tq.conns) ? tq.conns : []
    const c = (arr || []).find((x) => x.id === consoleModal.connId)
    if (!c) return ''
    const user = c.user || '-'
    const ip = c.ip || '-'
    const port = c.port || '-'
    return `${user}@${ip}:${port}`
  } catch { return '' }
})

async function openConsole(connId) {
  consoleModal.connId = connId
  consoleModal.open = true
  // 确保票据查询上下文初始化
  try { await ensureTicketInit() } catch {}
  // 再次同步连接列表
  try { await loadConnsFromModule() } catch {}
  // 确保工单查询模块可见的连接列表存在
  if (!tq.conns || !Array.isArray(tq.conns) || !tq.conns.length) {
    try { tq.conns = Array.isArray(list?.value) ? [...list.value] : (tq.conns || []) } catch { tq.conns = tq.conns || [] }
  }
  // 若仍不存在目标连接，尝试拉取单个连接
  try {
    const exists = (tq.conns || []).some(c => c.id === connId)
    if (!exists) {
      api.get(`/connections/${connId}`).then(({ data }) => {
        try {
          if (!tq.conns) tq.conns = []
          const idx = tq.conns.findIndex(c => c.id === data.id)
          if (idx >= 0) tq.conns[idx] = data; else tq.conns.push(data)
        } catch {}
      }).catch(() => {})
    }
  } catch {}

  // 选择目标连接并清理数据库选择与过滤
  tq.selectedConnId = connId
  try {
    // 数据库与左侧树
    tq.selectedDbs = []
    tq.selectedDb = ''
    tq.filter = ''
    tq.leftCollapsed = false
    tq.dbSearch = ''
    tq.expandedDb = {}
    tq.tableFilters = {}
    // 查询与分页
    tq.sql = ''
    tq.result = null
    tq.page = 1
    tq.pageInput = 1
    tq.pageSize = tq.pageSize || 50
    tq.totalRows = 0
    tq.respectInnerLimit = false
    // 表格列配置
    tq.tableColWidths = []
    tq.freezeCount = 0
    tq.freezeLefts = []
    tq.sortKey = ''
    tq.sortDir = ''
  } catch {}
  // 重置 SQL 标签为单个默认标签，避免保留上次会话的多个标签
  try {
    const id = 'tab-' + Date.now()
    tq.qTabs = [{ id, title: 'SQL 1', ui: { dirty: false } }]
    tq.activeQueryTabId = id
  } catch {}
  await onConnChange()
  // 初始化编辑器
  ensureSqlEditor()
  try {
    // 清空编辑器可视内容，避免复用
    if (tqEditorView) {
      const len = tqEditorView.state.doc.length
      if (len > 0) tqEditorView.dispatch({ changes: { from: 0, to: len, insert: '' } })
    }
  } catch {}
  // 设定编辑器默认高度，支持后续拖拽调整（允许从 0 起步，方便最小化）
  if (typeof tq.editorHeight !== 'number') tq.editorHeight = 150
}

function closeConsole() {
  consoleModal.open = false
}
// 提前声明会被 watch 立即读取的 ref，避免 TDZ 报错
const tqCodeRef = ref(null)
let tqEditorView = null
// 结果表格/滚动相关 refs（由子组件挂载时回传）
const tqHeadTableRef = ref(null)
const tqBodyTableRef = ref(null)
const tqScrollXRef = ref(null)
const tqBodyRef = ref(null)
// 右侧面板与主容器 refs（用于计算可拖拽高度范围）
// 注意：tqRightRef 在文件后部已有声明，这里不再重复声明
// 注意：避免重复声明，若下方已有同名定义，请仅保留一处
// 提前声明 tabs/activeTab，避免在早期 onMounted/watch 里访问时报 TDZ
const tabs = ref([{ key: 'conn', title: '连接管理' }])
const activeTab = ref('conn')
// 顶部信息栏 refs（提早声明以供后续使用）
const dateTimeText = ref('')
const lunarText = ref('')
const weatherText = ref('')
const adviceText = ref('')
// 农历库与调试标记（后续 ensureLunarLib 会引用）
let lunarModule = null
const DEBUG_LUNAR = false
// 提前声明 tq，避免在函数/监听里访问时报 TDZ
const tq = reactive({})
// 初始化与安全默认值（避免未定义导致的联动影响）
// 仅当显式启用 forceTreeFilter 且多选≥2时，左侧树才按多选过滤
if (tq) {
  tq.dbDropdownOpen = false
  tq.selectedDbs = []
  tq.selectedDb = ''
  tq.forceTreeFilter = false
  tq.expandedDb = {}
  tq.tables = {}
  tq.tablesLoading = {}
  tq.dbPanelHover = false
  // 多标签：初始化字段（复用现有全局状态以最小化改动）
  tq.qTabs = []
  tq.activeQueryTabId = ''
}

// 头体滚动同步：正文滚动时，驱动表头水平位移
function onBodyScroll(e) {
  try {
    const x = e?.target?.scrollLeft || 0
    const head = tqScrollXRef.value
    if (head && head.scrollLeft !== x) head.scrollLeft = x
    tq.bodyScrollX = x
  } catch {}
}

// 垂直分割：拖动调整编辑器与结果区高度
function startEditorVResize(e) {
  try {
    const right = tqRightRef?.value
    if (!right) return
    const rect = right.getBoundingClientRect()
    const startY = e.clientY
    const startH = Math.max(0, Number(tq.editorHeight || 0))
    const minEditor = 0
    const minResult = 140
    const maxEditor = Math.max(minEditor, rect.height - minResult)
    const onMove = (ev) => {
      const dy = ev.clientY - startY
      let h = startH + dy
      if (h < minEditor) h = minEditor
      if (h > maxEditor) h = maxEditor
      tq.editorHeight = Math.round(h)
      // 立刻同步容器与 CodeMirror 的高度，确保拖动过程中实时生效
      try {
        const editorEl = tqEditorRef?.value
        if (editorEl) {
          const px = Math.max(0, tq.editorHeight) + 'px'
          editorEl.style.height = px
          editorEl.style.flexBasis = px
          editorEl.style.setProperty('--tq-editor-h', px)
        }
        if (tqEditorView) {
          const px = Math.max(0, tq.editorHeight) + 'px'
          tqEditorView.dom.style.height = px
          tqEditorView.scrollDOM.style.height = px
        }
      } catch {}
      ev.preventDefault()
    }
    const onUp = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      document.body.style.userSelect = ''
      document.body.style.cursor = ''
      // 结束时再请求一次测量，巩固布局
      try { tqEditorView && typeof tqEditorView.requestMeasure === 'function' && tqEditorView.requestMeasure() } catch {}
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'ns-resize'
    e.preventDefault()
  } catch {}
}

// 编辑器高度变化后，通知 CodeMirror 重新测量布局
watch(() => tq.editorHeight, async () => {
  await nextTick()
  try { tqEditorView && typeof tqEditorView.requestMeasure === 'function' && tqEditorView.requestMeasure() } catch {}
})

// 通用：按候选路径依次尝试 GET，直到成功或全部失败
async function getWithFallback(paths, config) {
  let lastErr
  for (const p of paths) {
    try {
      const resp = await api.get(p, config)
      if (resp && resp.status >= 200 && resp.status < 300) return resp
    } catch (e) {
      lastErr = e
      // 若为 404/405 继续尝试下一个；其他错误直接抛出
      const code = e?.response?.status
      if (code && code !== 404 && code !== 405) throw e
    }
  }
  throw lastErr || new Error('all endpoints failed')
}

// --- 列排序与表头锁定交互 ---
// moved below after tq initialization

function toggleSort(col) {
  try {
    if (tq.sortKey !== col) {
      tq.sortKey = col
      tq.sortDir = 'asc'
    } else if (tq.sortDir === 'asc') {
      tq.sortDir = 'desc'
    } else if (tq.sortDir === 'desc') {
      tq.sortKey = ''
      tq.sortDir = ''
    } else {
      tq.sortDir = 'asc'
    }
  } catch {}
}

// 当结果集、分页、排序或冻结数量变化后，在下一帧统一重算列宽与滚动条补偿，避免硬刷新或快速操作导致 sticky 偏移失准
/* watcher moved below after tq initialization */

function getDisplayedRows() {
  try {
    const rows = (tq.result && tq.result.type === 'table' && Array.isArray(tq.result.rows)) ? tq.result.rows : []
    if (!tq.sortKey || !tq.sortDir) return rows
    const key = tq.sortKey
    const dir = tq.sortDir === 'asc' ? 1 : -1
    const copy = rows.slice()
    const colIndex = Array.isArray(tq.result.columns) ? tq.result.columns.indexOf(key) : -1
    copy.sort((a, b) => {
      const isArrayRow = Array.isArray(a) && Array.isArray(b)
      const va = isArrayRow && colIndex >= 0 ? a[colIndex] : a?.[key]
      const vb = isArrayRow && colIndex >= 0 ? b[colIndex] : b?.[key]
      if (va == null && vb == null) return 0
      if (va == null) return -1 * dir
      if (vb == null) return 1 * dir
      const na = typeof va === 'number' || (typeof va === 'string' && /^-?\d+(\.\d+)?$/.test(va))
      const nb = typeof vb === 'number' || (typeof vb === 'string' && /^-?\d+(\.\d+)?$/.test(vb))
      if (na && nb) return (Number(va) - Number(vb)) * dir
      const sa = String(va)
      const sb = String(vb)
      return sa.localeCompare(sb) * dir
    })
    return copy
  } catch { return (tq.result?.rows) || [] }
}

// 工具：判断事件是否发生在元素内部（兼容 Shadow DOM）
function isEventInside(el, ev) {
  try {
    if (!el || !ev) return false
    const path = typeof ev.composedPath === 'function' ? ev.composedPath() : null
    if (Array.isArray(path) && path.length) {
      return path.includes(el)
    }
    const t = ev.target
    return !!(t && el.contains(t))
  } catch { return false }
}

// 点击组件外部关闭数据库下拉面板
function onDocClickToCloseDb(ev) {
  try {
    if (!tq.dbDropdownOpen) return
    const root = tqDbMultiRef.value
    if (!root) return
    if (isEventInside(root, ev)) return
    tq.dbDropdownOpen = false
  } catch {}
}

// 窗口滚动时尝试关闭下拉：在面板内或指针悬停时不关闭
function onWindowScrollToCloseDb(ev) {
  try {
    if (!tq.dbDropdownOpen) return
    // 仅当页面（document/body/html）本身滚动时才关闭；
    // 列表等内部滚动不处理
    const t = ev && ev.target
    if (t && t !== window && t !== document && t !== document.documentElement && t !== document.body) return
    tq.dbDropdownOpen = false
  } catch {}
}

// 文档级捕获：捕捉对 .tq-sql 的点击，强制初始化编辑器（防止局部点击绑定未生效）
function onDocClickInitSql(ev) {
  try {
    const host = tqCodeRef.value || document.querySelector('.tq-sql')
    if (!host) return
    const inside = isEventInside(host, ev)
    if (!inside) return
    if (!tqEditorView) {
      try { console.log('[ticket.query] doc-capture: click .tq-sql -> ensureSqlEditor()') } catch {}
      try { ensureSqlEditor() } catch {}
    }
  } catch {}
}

onMounted(() => {
  try {
    document.addEventListener('mousedown', onDocClickToCloseDb, true)
    document.addEventListener('click', onDocClickToCloseDb, true)
    document.addEventListener('touchstart', onDocClickToCloseDb, true)
    // 捕获阶段监听，确保任何情况下点击 .tq-sql 都会触发初始化
    document.addEventListener('click', onDocClickInitSql, true)
    window.addEventListener('blur', () => { tq.dbDropdownOpen = false })
    window.addEventListener('resize', () => { tq.dbDropdownOpen = false })
    // 监听冒泡阶段，避免捕获阶段截获子元素滚动
    window.addEventListener('scroll', onWindowScrollToCloseDb, false)
    // 键盘 Esc 关闭
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') tq.dbDropdownOpen = false }, true)
  } catch {}
})

// 初次进入页面时，如果当前就在工单查询页，立即初始化编辑器
onMounted(async () => {
  try {
    if (activeTab.value === 'ticket.query') await ensureSqlEditor()
    // 初始：确保存在至少一个查询标签
    if (!Array.isArray(tq.qTabs) || tq.qTabs.length === 0) {
      newQueryTab()
    } else if (!tq.activeQueryTabId && tq.qTabs.length) {
      activateQueryTab(tq.qTabs[0].id)
    }
  } catch {}
})

// 当编辑器 DOM 节点挂载后（例如切换面板后）再补一次初始化，避免时序问题
watch(() => tqCodeRef.value, async (el) => {
  if (el && activeTab.value === 'ticket.query') {
    await ensureSqlEditor()
  }
})

function focusSqlEditor() {
  try {
    if (tqEditorView) {
      console.log('[ticket.query] focusSqlEditor: focusing editor')
      tqEditorView.focus()
    }
  } catch {}
}

async function onSqlHostClick() {
  try {
    if (!tqEditorView) {
      console.log('[ticket.query] onSqlHostClick -> init editor')
      await ensureSqlEditor()
    }
    focusSqlEditor()
  } catch {}
}

// --- 多标签：工具与方法 ---
let __tabSeq = 1
function makeTabTitle() { return `SQL ${__tabSeq++}` }
function getActiveTab() { return (tq.qTabs || []).find(t => t.id === tq.activeQueryTabId) || null }

function syncActiveTabFromGlobals() {
  const tab = getActiveTab(); if (!tab) return
  tab.sql = tq.sql || ''
  tab.result = tq.result || null
  tab.running = !!tq.running
  tab.page = tq.page || 1
  tab.pageSize = tq.pageSize || 50
  tab.totalRows = tq.totalRows || 0
  tab.respectInnerLimit = !!tq.respectInnerLimit
  // 将当前列冻结数写回到当前标签
  if (!tab.ui) tab.ui = {}
  tab.ui.freezeCount = tq.freezeCount || 0
}
function syncGlobalsFromTab(tab) {
  if (!tab) return
  tq.sql = tab.sql || ''
  tq.result = tab.result || null
  tq.running = !!tab.running
  tq.page = tab.page || 1
  tq.pageSize = tab.pageSize || 50
  tq.totalRows = tab.totalRows || 0
  tq.respectInnerLimit = !!tab.respectInnerLimit
  // 从标签恢复列冻结数至全局
  tq.freezeCount = (tab.ui && typeof tab.ui.freezeCount === 'number') ? tab.ui.freezeCount : 0
  nextTick(() => {
    try {
      if (tqEditorView) {
        const cur = tqEditorView.state.doc.toString()
        const target = tq.sql || ''
        if (cur !== target) {
          tqEditorView.dispatch({ changes: { from: 0, to: cur.length, insert: target } })
        }
        tqEditorView.focus()
      }
    } catch {}
  })
}

function newQueryTab() {
  const id = 'q' + Date.now() + Math.floor(Math.random()*1000)
  const tab = {
    id,
    title: makeTabTitle(),
    sql: '',
    result: null,
    running: false,
    page: 1,
    pageSize: 50,
    totalRows: 0,
    respectInnerLimit: false,
    ui: { dirty: false, resultCollapsed: false, splitRatio: 0.6, freezeCount: 0 }
  }
  if (!Array.isArray(tq.qTabs)) tq.qTabs = []
  tq.qTabs.push(tab)
  activateQueryTab(id)
}
function activateQueryTab(id) {
  if (!id) return
  // 先把当前全局状态写回原激活标签
  syncActiveTabFromGlobals()
  tq.activeQueryTabId = id
  const tab = getActiveTab()
  syncGlobalsFromTab(tab)
  // 确保编辑器存在
  nextTick(() => { try { ensureSqlEditor() } catch {} })
}
function closeQueryTab(id) {
  const idx = (tq.qTabs || []).findIndex(t => t.id === id)
  if (idx < 0) return
  const closingActive = (tq.activeQueryTabId === id)
  tq.qTabs.splice(idx, 1)
  if (!tq.qTabs.length) {
    // 若都没了，新建一个
    newQueryTab()
    return
  }
  if (closingActive) {
    const nextIdx = Math.max(0, Math.min(idx, tq.qTabs.length - 1))
    activateQueryTab(tq.qTabs[nextIdx].id)
  }
}

// 提供给子组件的上下文将在 refs 声明之后注入，见下文

// 在 SQL 文本变化时标记当前标签为 dirty
watch(() => tq.sql, (v) => {
  const tab = getActiveTab(); if (!tab) return
  tab.sql = v || ''
  if (tab.ui) tab.ui.dirty = true
})

// 执行/分页/查看计划/停止 后，把全局状态同步回当前标签
function _afterQueryStateChanged() {
  const tab = getActiveTab(); if (!tab) return
  tab.result = tq.result || null
  tab.running = !!tq.running
  tab.page = tq.page || 1
  tab.pageSize = tq.pageSize || 50
  tab.totalRows = tq.totalRows || 0
  tab.respectInnerLimit = !!tq.respectInnerLimit
  if (tab.ui) tab.ui.dirty = false
}

// 初始化 CodeMirror 编辑器
async function ensureSqlEditor() {
  await nextTick()
  try {
    console.log('[ticket.query] ensureSqlEditor: start')
    if (typeof window !== 'undefined') {
      window.__tqEnsureCalled = (window.__tqEnsureCalled || 0) + 1
    }
  } catch {}
  let host = tqCodeRef.value
  if (!host) {
    try {
      console.log('[ticket.query] ensureSqlEditor: host not found (tqCodeRef empty) -> try .tq-sql fallback')
      const fb = document.querySelector('.tq-sql')
      if (fb) {
        host = fb
        fb.dataset.nohost = '0'
        fb.style.outline = fb.style.outline || '2px dashed #ff7875'
      }
    } catch {}
  }
  if (!host) { try { console.log('[ticket.query] ensureSqlEditor: still no host, abort') } catch {} ; return }
  // 若编辑器已存在，但 DOM 未挂到当前 host（例如组件重渲染后 .tq-sql 重新生成），则把现有编辑器 DOM 迁移到新容器
  if (tqEditorView) {
    try {
      const parent = tqEditorView.dom?.parentElement
      if (parent !== host) {
        try { console.log('[ticket.query] ensureSqlEditor: reparent editor to new host') } catch {}
        try { host.appendChild(tqEditorView.dom) } catch {}
        try { host.dataset.inited = '1' } catch {}
        try { tqEditorView.focus() } catch {}
      } else {
        try { console.log('[ticket.query] ensureSqlEditor: already inited') } catch {}
      }
    } catch {}
    return
  }
  try {
  // 保障容器可见且可聚焦
    host.tabIndex = 0
  // 允许最小高度为 0，配合分割条可完全收起
  host.style.minHeight = '0px'
    host.style.outline = host.style.outline || '2px solid #7db3ff44'
    host.style.borderRadius = host.style.borderRadius || '6px'
  } catch {}

  // 自动补全源：关键词 + 动态库/表/列
  const KEYWORDS = [
    'SELECT','FROM','WHERE','JOIN','LEFT','RIGHT','INNER','OUTER','GROUP BY','ORDER BY','LIMIT','INSERT','UPDATE','DELETE','CREATE','ALTER','DROP','USE','AND','OR','NOT','IN','BETWEEN','LIKE','IS NULL','IS NOT NULL'
  ]

  const completionSource = async (ctx /** @type {CompletionContext} */) => {
    const before = ctx.state.sliceDoc(0, ctx.pos)
    const word = ctx.matchBefore(/[\w`.$]+/)
    const endsWithDot = /\.$/.test(before)
    if (!word && !ctx.explicit && !endsWithDot) return null

    const options = []

    // schema.table 或 table. => 表/列智能提示
    // 1) schema.            -> 列出该库所有表
    // 2) schema.part        -> 按 part 过滤表名，动态变化
    // 3) schema.table.      -> 列提示
    const mSchemaTable = before.match(/([`\w]+)\.([`\w]*)$/)
    if (mSchemaTable) {
      const schemaRaw = mSchemaTable[1]
      const partialRaw = mSchemaTable[2] || ''
      const schema = schemaRaw.replaceAll('`', '')
      const partial = partialRaw.replaceAll('`', '')

      // schema.table. -> 列提示（优先匹配带点结尾的列场景）
      const mColumns = before.match(/([`\w]+)\.([`\w]+)\.$/)
      if (mColumns) {
        const s = mColumns[1].replaceAll('`', '')
        const t = mColumns[2].replaceAll('`', '')
        const cols = await loadColumnsIfNeeded(s, t)
        for (const c of cols) options.push({ label: c, type: 'property' })
        return { from: ctx.pos, options }
      }

      // schema. 或 schema.part -> 表名提示（按前缀过滤，不混入其他类型）
      if (schema) {
        let allTables = getTablesBySchemaName(schema)
        if (!allTables.length) {
          allTables = await loadTablesIfNeeded(schema)
        }
        const lowerP = String(partial || '').toLowerCase()
        const filtered = lowerP
          ? allTables.filter(t => String(t).toLowerCase().includes(lowerP))
          : allTables
        for (const t of filtered) options.push({ label: String(t), type: 'table', apply: String(t) })
        // 仅替换 partial，不影响 "schema." 部分
        const from = ctx.pos - partialRaw.length
        return { from, options }
      }
    }

    // 基础关键词（仅在不处于 `schema.` 的专用场景时添加）
    for (const k of KEYWORDS) options.push({ label: k, type: 'keyword' })

    // 根据上下文推荐：schema.table 与 table.column
    const mPath = before.match(/([\w`]+(\.[\w`]+)*)$/)
    const path = mPath ? String(mPath[1]).replace(/`/g, '') : ''
    const parts = path ? path.split('.') : []

    // 数据库列表（schema）
    for (const db of (tq.databases || [])) options.push({ label: db, type: 'namespace' })

    // 若命中 schema. 则提示该库下表/视图（我们只有表名列表）
    if (parts.length === 1 && (tq.databases || []).includes(parts[0])) {
      const db = parts[0]
      const tables = tq.tables?.[db] || []
      for (const t of tables) options.push({ label: t, type: 'table' })
    }

    // 若命中 schema.table 或 alias. 列提示（仅在 schema.table 场景实现）
    if (parts.length >= 2) {
      const [maybeDb, maybeTbl] = parts.slice(-2)
      if ((tq.databases || []).includes(maybeDb)) {
        const cols = await loadColumnsIfNeeded(maybeDb, maybeTbl)
        for (const c of cols) options.push({ label: c, type: 'property' })
      }
    }

    let from = word ? word.from : ctx.pos
    // 在输入了 schema. 之后弹出表名列表，不替换掉 `schema.` 本身
    if (endsWithDot) from = ctx.pos
    return { from, options }
  }

  // 懒加载列缓存：tq.columnsCache: { 'db.table': string[] }
  if (!tq.columnsCache) tq.columnsCache = {}
  async function loadColumnsIfNeeded(db, tbl) {
    const key = `${db}.${tbl}`
    if (tq.columnsCache[key]) return tq.columnsCache[key]
    if (!tq.selectedConnId || !db || !tbl) return []
    try {
      const params = { connId: tq.selectedConnId, connectionId: tq.selectedConnId, conn_id: tq.selectedConnId, id: tq.selectedConnId, db, database: db, schema: db, table: tbl, tableName: tbl, tbl }
      const { data } = await api.get('/ticket/columns', { params })
      const arr = Array.isArray(data) ? data : []
      tq.columnsCache[key] = arr
      return arr
    } catch (_) {
      return []
    }
  }

  // 懒加载库下表：tq.tables[schema] => string[]
  async function loadTablesIfNeeded(schema) {
    if (!schema) return []
    // 已有缓存
    let cached = getTablesBySchemaName(schema)
    if (cached && cached.length) return cached
    try {
      // 使用与 columns 相同的 api 客户端与参数，确保命中后端 JSON
      if (!tq.selectedConnId) return []
      const params = { connId: tq.selectedConnId, connectionId: tq.selectedConnId, conn_id: tq.selectedConnId, id: tq.selectedConnId, db: schema, database: schema, schema }
      const { data } = await api.get('/ticket/tables', { params })
      const list = normalizeTableList(Array.isArray(data) ? data : (Array.isArray(data?.data) ? data.data : []))
      if (!tq.tables) tq.tables = {}
      // 直接以传入 schema 作为键保存，避免大小写再次查找
      tq.tables[schema] = list
      return list
    } catch (e) {
      console.warn('[ticket.query] loadTablesIfNeeded failed:', e)
      return []
    }
  }

  // 按库名获取表列表：支持大小写不敏感匹配与对象数组
  function getTablesBySchemaName(name) {
    const map = tq.tables || {}
    if (!name) return []
    if (map[name]) return normalizeTableList(map[name])
    const hitKey = Object.keys(map).find(k => String(k).toLowerCase() === String(name).toLowerCase())
    return hitKey ? normalizeTableList(map[hitKey]) : []
  }

  function normalizeTableList(list) {
    if (!Array.isArray(list)) return []
    return list.map(v => {
      if (typeof v === 'string') return v
      if (v && typeof v === 'object') {
        return v.name || v.table || v.table_name || v.TABLE_NAME || v.value || v.label || String(Object.values(v)[0])
      }
      return String(v)
    }).filter(Boolean)
  }

  const extensions = [
    sql({ dialect: MySQL }),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
    autocompletion({ override: [completionSource], activateOnTyping: true, maxRenderedOptions: 200 }),
    keymap.of([
      { key: 'Ctrl-Enter', run: () => { try { executeSQL() } catch {} return true } },
      { key: 'Mod-Enter', run: () => { try { executeSQL() } catch {} return true } },
    ]),
    highlightActiveLine(),
    EditorView.lineWrapping,
    EditorView.updateListener.of((v) => {
      if (v.docChanged) {
        tq.sql = v.state.doc.toString()
      }
    }),
  ]

  tqEditorView = new EditorView({
    state: EditorState.create({
      doc: tq.sql || '',
      extensions,
    }),
    parent: host,
  })
  try { console.log('[ticket.query] ensureSqlEditor: created EditorView', { len: tqEditorView.state.doc.length }) } catch {}
  try { tqEditorView.focus() } catch {}
  try { host.dataset.inited = '1' } catch {}
  try { if (typeof window !== 'undefined') { window.__tqEditorView = tqEditorView } } catch {}
  try {
    // 强化可见性与点击性（内联，避免被外层样式覆盖）
    const root = host.querySelector('.cm-editor')
    if (root) {
      // 允许最小高度为 0
      root.style.minHeight = '0px'
      root.style.background = root.style.background || '#fff'
      root.style.border = root.style.border || '1px solid #dcdfe6'
      root.style.borderRadius = root.style.borderRadius || '6px'
      root.style.pointerEvents = 'auto'
      root.style.position = root.style.position || 'relative'
      // 降低层级，避免遮挡结果表头
      root.style.zIndex = '1'
    }
  } catch {}
}

// 当切换到工单查询时初始化编辑器；并保持内容同步
// 兜底：在模块加载后尝试多次初始化（容器未就绪时会安全返回）
try {
  if (typeof window !== 'undefined') {
    // 暴露手动触发入口到多全局：window / globalThis
    try { window.__tqEnsure = ensureSqlEditor } catch {}
    try { (globalThis).__tqEnsure = ensureSqlEditor } catch {}
    try { document.documentElement && (document.documentElement.dataset.tqExpose = '1') } catch {}
    try { console.log('[ticket.query] expose ensure ->', typeof window.__tqEnsure, typeof (globalThis).__tqEnsure) } catch {}
    // 再异步一次，避免某些初始化顺序问题
    try { setTimeout(() => { try { window.__tqEnsure = ensureSqlEditor; (globalThis).__tqEnsure = ensureSqlEditor } catch {} }, 0) } catch {}
  }
  setTimeout(() => { ensureSqlEditor() }, 0)
  setTimeout(() => { ensureSqlEditor() }, 300)
  setTimeout(() => { ensureSqlEditor() }, 1000)
  // 观察 .tq-sql 容器是否动态出现，出现即初始化（一次性）
  const mo = new MutationObserver(() => {
    const el = document.querySelector('.tq-sql')
    if (el && !el.dataset.inited) {
      console.log('[ticket.query] MutationObserver: .tq-sql appeared, ensure init')
      ensureSqlEditor()
    }
  })
  try { mo.observe(document.documentElement, { childList: true, subtree: true }) } catch {}
  // 周期性兜底重试，最多尝试 20 次（约 10 秒）
  let __tqTries = 0
  const __tqTimer = setInterval(() => {
    if (tqEditorView) { clearInterval(__tqTimer); return }
    __tqTries++
    console.log('[ticket.query] interval ensure try', __tqTries)
    ensureSqlEditor()
    if (__tqTries >= 20) clearInterval(__tqTimer)
  }, 500)
} catch {}
watch(() => activeTab.value, async (tab) => {
  if (tab === 'ticket.query') {
    await ensureSqlEditor()
    if (tqEditorView && tq.sql !== tqEditorView.state.doc.toString()) {
      tqEditorView.dispatch({
        changes: { from: 0, to: tqEditorView.state.doc.length, insert: tq.sql || '' }
      })
    }
  }
})

// 当外部逻辑修改 tq.sql 时，同步到编辑器（避免双向死循环，判断差异）
watch(() => tq.sql, (val) => {
  if (!tqEditorView) return
  const cur = tqEditorView.state.doc.toString()
  if (val !== cur) {
    tqEditorView.dispatch({ changes: { from: 0, to: cur.length, insert: val || '' } })
  }
})

onBeforeUnmount(() => {
  try {
    document.removeEventListener('mousedown', onDocClickToCloseDb, true)
    document.removeEventListener('click', onDocClickToCloseDb, true)
    document.removeEventListener('touchstart', onDocClickToCloseDb, true)
    document.removeEventListener('click', onDocClickInitSql, true)
  } catch {}
})

function headerLockClick(i) {
  try {
    const nCols = tq.result?.columns?.length || 0
    if (!nCols) return
    const current = Math.max(0, Math.min(tq.freezeCount || 0, nCols))
    // 只能从左至右锁定：点击第 i 列，将冻结数设为 i+1；如果点击的是当前最后一个冻结列，则减少为 i（解锁最后一列）
    if (i < current - 1) {
      // 点击已冻结但非最后一列，不做跳跃处理，只保证前缀冻结
      tq.freezeCount = i + 1
    } else if (i === current - 1) {
      tq.freezeCount = i // 解锁最后一列
    } else {
      tq.freezeCount = i + 1
    }
    // 先立即按当前可得宽度回算冻结位移，避免瞬时 left=0 导致标题看似“消失”；随后在下一帧统一重算列宽与位移
    recomputeFrozenOffsets()
    nextTick().then(() => { computeColWidths(); adjustHeaderGutter() })
  } catch {}
}

const list = ref([])
const formKey = ref(0)
const showModal = ref(false)
const activeMenu = ref('conn')
const dataMenuOpen = ref(false)
// 侧边栏折叠
const sidebarCollapsed = ref(false)
const layoutStyle = computed(() => ({}))
// 顶部信息栏 & 标签页
// 删除确认弹窗状态
const confirmVisible = ref(false)
const confirmItem = ref(null)
const confirmText = ref('')
async function ensureLunarLib() {
  if ((window).solarlunar || (window).solarLunar || (window).SolarLunar) return 'sl'
  if ((window).Solar) return 'lj'
  if (lunarModule) return 'lj'
  // 0) 优先尝试本地 solarlunar（API 简单稳定：solar2lunar）
  try {
    if (DEBUG_LUNAR) try { console.log('[Lunar] ensureLunarLib: try local package import "solarlunar"') } catch {}
    const mod = await import('solarlunar')
    const sl = (mod && (mod.default || mod)) || null
    if (sl && (sl.solar2lunar || sl['solar2lunar'])) {
      ;(window).solarlunar = sl
      if (DEBUG_LUNAR) try { console.log('[Lunar] ensureLunarLib: solarlunar loaded locally. has solar2lunar =', typeof sl.solar2lunar === 'function') } catch {}
      return 'sl'
    }
  } catch (_) { /* 转入后续兜底 */ }
  if (DEBUG_LUNAR) try { console.warn('[Lunar] ensureLunarLib: solarlunar not available locally') } catch {}
  return null
}

function openTab(key, title) {
  if (!tabs.value.find(t => t.key === key)) {
    tabs.value.push({ key, title })
  }
  activeTab.value = key
}
function switchTab(key) { activeTab.value = key }
function closeTab(key) {
  const idx = tabs.value.findIndex(t => t.key === key)
  if (idx !== -1) {
    tabs.value.splice(idx, 1)
    // 关闭当前活动页则切换到相邻页或默认首页
    if (activeTab.value === key) {
      const next = tabs.value[idx] || tabs.value[idx - 1] || tabs.value[0]
      activeTab.value = next ? next.key : ''
    }
  }
}

function pad(n) { return n.toString().padStart(2, '0') }
let lunarTries = 0
let lastLoggedMinute = -1
let lunarLoggedOnce = false
function updateDateTime() {
  const d = new Date()
  const y = d.getFullYear()
  const m = d.getMonth() + 1
  const day = d.getDate()
  const h = pad(d.getHours())
  const mi = pad(d.getMinutes())
  const s = pad(d.getSeconds())
  const weekMap = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六']
  const week = weekMap[d.getDay()]
  dateTimeText.value = `${y}年${m}月${day}日 ${h}:${mi}:${s} ${week}`
  // 分钟级节流输出日期时间
  if (d.getMinutes() !== lastLoggedMinute) {
    lastLoggedMinute = d.getMinutes()
    if (DEBUG_LUNAR) try { console.log(`[时间] ${dateTimeText.value}`) } catch {}
  }
  try {
    // 多种命名兼容
    const SL = (window).solarlunar || (window)['solarlunar'] || (window).solarLunar || (window)['solarLunar'] || (window).SolarLunar
    if (SL && typeof SL.solar2lunar === 'function') {
      const lunar = SL.solar2lunar(y, m, day)
      lunarText.value = `农历${lunar.monthCn}${lunar.dayCn}`
      if (DEBUG_LUNAR) try { console.log('[Lunar] branch: solarlunar.solar2lunar ->', lunarText.value) } catch {}
    } else {
      lunarText.value = '农历--'
    }
  } catch (e) {
    lunarText.value = '农历--'
    if (DEBUG_LUNAR) try { console.warn('[Lunar] compute error:', e) } catch {}
  }
  // 农历首次成功时立即输出到控制台
  if (lunarText.value && lunarText.value !== '农历--' && !lunarLoggedOnce) {
    lunarLoggedOnce = true
    if (DEBUG_LUNAR) try { console.log(`[农历] ${lunarText.value}`) } catch {}
  }
  // 如果外部库尚未加载成功，重试几次
  if (lunarText.value === '农历--' && lunarTries < 20) {
    lunarTries += 1
    // 先尝试动态加载库，再重试
    if (DEBUG_LUNAR) try { console.log('[Lunar] retry', lunarTries, '-> ensureLunarLib() then re-run') } catch {}
    ensureLunarLib().finally(() => setTimeout(updateDateTime, 800))
  }
}

// 繁转简（轻量常用字映射）
function toSimplified(str) {
  if (!str) return ''
  const map = {
    '區':'区','縣':'县','鄉':'乡','鎮':'镇','陽':'阳','陰':'阴','東':'东','西':'西','南':'南','北':'北',
    '臺':'台','颱':'台','溫':'温','濕':'湿','風':'风','雲':'云','霧':'雾','電':'电','氣':'气','體':'体',
    '雖':'虽','與':'与','為':'为','於':'于','這':'这','轉':'转','裝':'装','續':'续','顏':'颜','數':'数',
    '廣':'广','長':'长','門':'门','國':'国','書':'书','車':'车','醫':'医','參':'参','週':'周','礦':'矿',
    '畫':'画','較':'较','價':'价','館':'馆','應':'应','檢':'检','簡':'简','網':'网','線':'线','針':'针'
  }
  return String(str).split('').map(ch => map[ch] || ch).join('')
}

function normalizeCnName(s) {
  if (!s) return ''
  return toSimplified(String(s))
    .replace(/\s+/g, '')
    .replace(/特别行政区$/,'')
    .replace(/自治区$/,'')
    .replace(/省$/,'')
    .replace(/市$/,'')
}

function composeCn(province, city, district) {
  const muni = ['北京','天津','上海','重庆']
  const sar = ['香港','澳门']
  const p = normalizeCnName(province)
  const cRaw = normalizeCnName(city)
  const d = normalizeCnName(district)

  // 特别行政区：不加“市/省”后缀
  if (sar.includes(p)) {
    // 优先显示 区/县；若无则显示城市
    const cityText = cRaw && (cRaw.endsWith('市') ? cRaw : cRaw + '市')
    const parts = [p, d || cityText]
    return toSimplified(parts.filter(Boolean).join(' '))
  }

  // 直辖市：使用“北京市 朝阳区”样式（不重复城市名）
  if (muni.includes(p) || p === cRaw) {
    const pText = p.endsWith('市') ? p : p + '市'
    return toSimplified([pText, d].filter(Boolean).join(' '))
  }

  // 普通省份：省 + 市 + 区/县
  const provText = p ? (p.endsWith('省') ? p : p + '省') : ''
  const cityText = cRaw ? (cRaw.endsWith('市') ? cRaw : cRaw + '市') : ''
  return toSimplified([provText, cityText, d].filter(Boolean).join(' '))
}

async function reverseGeocode(lat, lon) {
  // fetch 超时控制（3s）
  const withTimeout = (input, init) => {
    const controller = new AbortController()
    const id = setTimeout(() => controller.abort('timeout'), 3000)
    const merged = Object.assign({}, init || {}, { signal: controller.signal })
    return fetch(input, merged).finally(() => clearTimeout(id))
  }
  // 1) Open‑Meteo
  try {
    const geoUrl = `/open-meteo-geo/v1/reverse?latitude=${lat}&longitude=${lon}&language=zh-CN&format=json`
    const geoResp = await withTimeout(geoUrl)
    if (geoResp.ok) {
      const geo = await geoResp.json()
      const item = (geo && geo.results && geo.results[0]) || null
      if (item) {
        const province = item.admin1 || ''
        const city = item.admin2 || item.name || ''
        const district = item.admin3 || ''
        const txt = composeCn(province, city, district)
        if (txt) return txt
      }
    }
  } catch {}
  // 2) BigDataCloud
  try {
    const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=zh` 
    const r = await withTimeout(url)
    if (r.ok) {
      const j = await r.json()
      const province = j.principalSubdivision || ''
      const city = j.city || j.locality || ''
      const district = j.localityInfo?.administrative?.find(x=>x.adminLevel===6)?.name || ''
      const txt = composeCn(province, city, district)
      if (txt) return txt
    }
  } catch {}
  // 3) Nominatim (尽力而为)
  try {
    const geoUrl = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&accept-language=zh-CN`
    const geoResp = await withTimeout(geoUrl, { headers: { 'User-Agent': 'db_expert_ui' } })
    if (geoResp.ok) {
      const geoData = await geoResp.json()
      const addr = geoData?.address || {}
      const province = addr.state || addr.province || ''
      const city = addr.city || addr.town || addr.village || addr.municipality || ''
      const district = addr.county || addr.district || addr.suburb || ''
      const txt = composeCn(province, city, district)
      if (txt) return txt
    }
  } catch {}
  return ''
}

async function fetchWeather(posOpt) {
  // 特殊含义：posOpt === null 表示显式触发“IP 定位兜底”
  try {
    if (posOpt === null) {
      try { console.log('[Weather] 使用 IP 兜底定位') } catch {}
      let ipLat = null, ipLon = null, ipLoc = ''
      try {
        const ipResp = await fetch('https://ipapi.co/json/')
        if (ipResp.ok) {
          const ipJson = await ipResp.json()
          ipLat = Number(ipJson.latitude)
          ipLon = Number(ipJson.longitude)
          const region = ipJson.region || ''
          const city = ipJson.city || ''
          ipLoc = toSimplified(`${region}${city}`)
        }
      } catch (e) { try { console.warn('[Weather] IP 定位失败', e) } catch {} }
      if (ipLat == null || ipLon == null) {
        // 兜底失败
        weatherText.value = ''
        adviceText.value = ''
        return
      }
      try {
        // 优先使用逆地理编码（中文、省市区），为空再退回 IP 接口返回的地域名
        const locText = (await reverseGeocode(ipLat, ipLon)) || ipLoc
        const url = `/open-meteo/v1/forecast?latitude=${ipLat}&longitude=${ipLon}&current=temperature_2m,precipitation,weather_code&timezone=auto`
        const resp = await fetch(url)
        if (!resp.ok) throw new Error('forecast http ' + resp.status)
        const data = await resp.json()
        const cur = data.current || {}
        const temp = cur.temperature_2m
        const prec = cur.precipitation
        const wcode = cur.weather_code
        const codeMap = { 0: '晴', 1: '多云', 2: '多云', 3: '阴', 45: '雾', 48: '雾', 51: '毛毛雨', 53: '小雨', 55: '中雨', 61: '小雨', 63: '中雨', 65: '大雨', 71: '小雪', 73: '中雪', 75: '大雪', 95: '雷阵雨' }
        const wtext = codeMap[wcode] || '天气'
        const locPrefix = toSimplified(locText || `${ipLat.toFixed(4)},${ipLon.toFixed(4)}`)
        const display = toSimplified(`${locPrefix} · 当前 ${wtext} ${temp}°C${prec ? `，降水 ${prec}mm` : ''}`)
        weatherText.value = display
        try { localStorage.setItem('weather_cache', JSON.stringify({ text: display, advice: adviceText.value, ts: Date.now() })) } catch {}
        const t = Number(temp)
        const advice = []
        if (t <= 5) advice.push('注意保暖')
        else if (t <= 15) advice.push('适度增添衣物')
        else if (t >= 28) advice.push('清凉出行，防暑降温')
        if (Number(prec) > 0) advice.push('备雨具，注意路滑')
        adviceText.value = advice.join('，') || '出行愉快'
      } catch (err) {
        try { console.warn('[Weather] IP 兜底获取天气失败', err) } catch {}
        weatherText.value = ''
        adviceText.value = ''
      }
      return
    }

    // 常规路径：浏览器 geolocation
    if (!navigator.geolocation && !posOpt) return
    const pos = posOpt || await new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        p => resolve(p),
        _ => resolve(null),
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
      )
    })
    if (!pos) { try { console.log('[Weather] 浏览器定位失败，触发 IP 兜底') } catch {}; setTimeout(() => fetchWeather(null), 0); return }
    const { latitude, longitude } = pos.coords
    try { console.log('[Weather] 首次定位', { lat: latitude, lon: longitude, acc: Number(pos?.coords?.accuracy) }) } catch {}
    try {
      // 反向地理编码，获取省市区/县（含多级回退）
      const locText = await reverseGeocode(latitude, longitude)

      const url = `/open-meteo/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,precipitation,weather_code&timezone=auto`
      const resp = await fetch(url)
      const data = await resp.json()
      const cur = data.current || {}
      const temp = cur.temperature_2m
      const prec = cur.precipitation
      const wcode = cur.weather_code
      const codeMap = {
        0: '晴', 1: '多云', 2: '多云', 3: '阴', 45: '雾', 48: '雾', 51: '毛毛雨', 53: '小雨', 55: '中雨',
        61: '小雨', 63: '中雨', 65: '大雨', 71: '小雪', 73: '中雪', 75: '大雪', 95: '雷阵雨'
      }
      const wtext = codeMap[wcode] || '天气'
      const locPrefix = toSimplified(locText || `${latitude.toFixed(4)},${longitude.toFixed(4)}`)
      const display = toSimplified(`${locPrefix} · 当前 ${wtext} ${temp}°C${prec ? `，降水 ${prec}mm` : ''}`)
      weatherText.value = display
      // 写入缓存
      try { localStorage.setItem('weather_cache', JSON.stringify({ text: display, advice: adviceText.value, ts: Date.now() })) } catch {}
      // 简单穿衣/出行建议
      const t = Number(temp)
      const advice = []
      if (t <= 5) advice.push('注意保暖')
      else if (t <= 15) advice.push('适度增添衣物')
      else if (t >= 28) advice.push('清凉出行，防暑降温')
      if (Number(prec) > 0) advice.push('备雨具，注意路滑')
      adviceText.value = advice.join('，') || '出行愉快'
    } catch (err) { /* 忽略 */ }

    // 如果初次定位精度较差，后台再尝试一次高精度定位以获得更准确的区县（不阻塞 UI）
    try {
      const acc = Number(pos?.coords?.accuracy)
      if ((Number.isNaN(acc) || acc > 1200) && navigator.geolocation) {
        // 二次高精度尝试（更长超时，不使用缓存）
        navigator.geolocation.getCurrentPosition(async p2 => {
          try {
            const acc2 = Number(p2?.coords?.accuracy)
            if (Number.isNaN(acc2) || acc2 >= acc) return
            const la2 = p2.coords.latitude
            const lo2 = p2.coords.longitude
            const loc2 = await reverseGeocode(la2, lo2)
            const url2 = `/open-meteo/v1/forecast?latitude=${la2}&longitude=${lo2}&current=temperature_2m,precipitation,weather_code&timezone=auto`
            const resp2 = await fetch(url2)
            if (!resp2.ok) return
            const data2 = await resp2.json()
            const cur2 = data2.current || {}
            const t2 = cur2.temperature_2m
            const pr2 = cur2.precipitation
            const wc2 = cur2.weather_code
            const codeMap2 = { 0: '晴', 1: '多云', 2: '多云', 3: '阴', 45: '雾', 48: '雾', 51: '毛毛雨', 53: '小雨', 55: '中雨', 61: '小雨', 63: '中雨', 65: '大雨', 71: '小雪', 73: '中雪', 75: '大雪', 95: '雷阵雨' }
            const wtxt2 = codeMap2[wc2] || '天气'
            const locPrefix2 = toSimplified(loc2 || `${la2.toFixed(4)},${lo2.toFixed(4)}`)
            const display2 = toSimplified(`${locPrefix2} · 当前 ${wtxt2} ${t2}°C${pr2 ? `，降水 ${pr2}mm` : ''}`)
            weatherText.value = display2
            // 更新建议与缓存
            const tnum = Number(t2)
            const adv = []
            if (tnum <= 5) adv.push('注意保暖')
            else if (tnum <= 15) adv.push('适度增添衣物')
            else if (tnum >= 28) adv.push('清凉出行，防暑降温')
            if (Number(pr2) > 0) adv.push('备雨具，注意路滑')
            adviceText.value = adv.join('，') || '出行愉快'
            try { localStorage.setItem('weather_cache', JSON.stringify({ text: display2, advice: adviceText.value, ts: Date.now() })) } catch {}
            try { console.log('[Weather] 高精度定位已更新显示，accuracy=', acc2) } catch {}
          } catch {}
        }, _e => { /* ignore */ }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 })
      }
    } catch {}
  } catch { /* 忽略 */ }
}

// 头像加载失败时的兜底处理
function onAvatarError(ev) {
  const img = ev?.target
  if (!img) return
  const steps = [
    'https://unpkg.com/emoji-datasource-apple/img/apple/64/1f431.png',
    'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f431.png',
    'https://unpkg.com/twemoji@14.0.2/assets/72x72/1f431.png'
  ]
  img.__fallbackStep = (img.__fallbackStep || 0) + 1
  const next = steps[img.__fallbackStep - 1]
  if (next) {
    img.src = next
    return
  }
  // 最后使用内联 SVG 作为占位，确保可见
  const svg = encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#fff" stroke="#d0d7de"/><text x="50%" y="54%" text-anchor="middle" font-size="28" font-family="Segoe UI Emoji">🐱</text></svg>')
  img.src = `data:image/svg+xml;charset=utf-8,${svg}`
}

onMounted(async () => {
  // 直接初始化（不等待 window 'load'），显著缩短首屏等待
  try {
    const cached = JSON.parse(localStorage.getItem('weather_cache') || 'null')
    if (cached && cached.text && Date.now() - cached.ts < 30 * 60 * 1000) {
      weatherText.value = cached.text
      if (cached.advice) adviceText.value = cached.advice
    }
  } catch {}
  // 预热加载农历库，减少首次“农历--”概率
  try { await ensureLunarLib() } catch {}
  updateDateTime()
  setInterval(updateDateTime, 1000)
  // 天气与定位：并行触发，且为 geolocation 设置 3s 竞争超时，避免阻塞首屏
  ;(async () => {
    // 记录权限状态，帮助排查为何浏览器定位没有返回
    try {
      if (navigator?.permissions?.query) {
        const st = await navigator.permissions.query({ name: 'geolocation' })
        try { console.log('[Weather] geolocation permission:', st.state) } catch {}
        st.onchange = () => { try { console.log('[Weather] geolocation permission changed:', st.state) } catch {} }
      }
    } catch {}
    const geoPromise = new Promise((resolve) => {
      let done = false
      try { console.log('[Weather] 发起首定位 (non-HA)') } catch {}
      const timer = setTimeout(() => { if (!done) { try { console.log('[Weather] 首定位超时(非HA)') } catch {}; done = true; resolve(null) } }, 8000)
      if (!navigator.geolocation) { clearTimeout(timer); resolve(null); return }
      navigator.geolocation.getCurrentPosition(
        pos => { if (!done) { done = true; clearTimeout(timer); resolve(pos) } },
        e => { try { console.log('[Weather] 首定位失败(HA):', e?.code, e?.message) } catch {}; if (!done) { done = true; clearTimeout(timer); resolve(null) } },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
      )
    })
    const pos = await geoPromise
    if (pos) {
      fetchWeather(pos)
    } else {
      // 立即触发 IP 兜底，不再等待
      setTimeout(() => fetchWeather(null), 0)
    }
    // 并发触发一次高精度定位（不依赖首次结果），若成功则用更准确坐标再次刷新显示
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          p2 => { try { console.debug('[Weather] 并发HA定位返回，accuracy=', p2?.coords?.accuracy) } catch {}; fetchWeather(p2) },
          e => { try { console.log('[Weather] 并发HA定位失败:', e?.code, e?.message) } catch {} },
          { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
        )
        // 再并发一个 watchPosition（HA），拿到首个定位后立刻清除，提升拿坐标概率
        try { console.log('[Weather] 启动 watchPosition(HA) 监听') } catch {}
        const watchId = navigator.geolocation.watchPosition(
          p3 => {
            try { console.log('[Weather] watchPosition 命中，accuracy=', p3?.coords?.accuracy) } catch {}
            try { navigator.geolocation.clearWatch(watchId) } catch {}
            fetchWeather(p3)
          },
          e3 => { try { console.log('[Weather] watchPosition 错误:', e3?.code, e3?.message) } catch {} },
          { enableHighAccuracy: true, maximumAge: 0 }
        )
        // 最多监听 15 秒，避免长期占用
        setTimeout(() => { try { navigator.geolocation.clearWatch(watchId) } catch {} }, 15000)
      }
    } catch {}
  })()
})
const filter = reactive({ type: '', env: '', status: '' })
const message = ref('')
// 全局 toast 提示
const globalNotices = ref([])
function addGlobalNotice(text, ttlMs = 3000) {
  const id = Date.now() + Math.random()
  globalNotices.value.push({ id, text })
  setTimeout(() => {
    const i = globalNotices.value.findIndex(n => n.id === id)
    if (i !== -1) globalNotices.value.splice(i, 1)
  }, ttlMs)
}
// 自动清空 message，并弹出全局 toast，避免被密码弹窗遮挡
watch(message, (v) => {
  if (v) {
    addGlobalNotice(v)
    setTimeout(() => { if (message.value === v) message.value = '' }, 3000)
  }
})
const editing = ref(false)
const editingId = ref(null)

// 分页
const page = ref(1)
const pageSize = ref(10)

// ================= 工单查询（ticket.query） =================
const tqMainRef = ref(null)
const tqContainerRef = ref(null)
const previewRef = ref(null)
const tqRightRef = ref(null)
// 计算右侧容器高度为视口减去其顶部偏移，保证上下区域可分配高度
function syncRightHeight() {
  const el = tqRightRef.value
  if (!el) return
  let h = 0
  try {
    const main = tqMainRef?.value
    if (main) {
      h = Math.floor(main.getBoundingClientRect().height)
    }
  } catch {}
  if (!h || h <= 0) {
    const rect = el.getBoundingClientRect()
    const viewportH = window.innerHeight || document.documentElement.clientHeight
    // 预留底部 16px 呼吸空间
    h = Math.floor(viewportH - rect.top - 16)
  }
  h = Math.max(420, h)
  el.style.height = h + 'px'
}
onMounted(() => {
  try { syncRightHeight() } catch {}
  try { window.addEventListener('resize', syncRightHeight) } catch {}
})
onBeforeUnmount(() => {
  try { window.removeEventListener('resize', syncRightHeight) } catch {}
})
const tqEditorRef = ref(null)
// tqCodeRef / tqEditorView 已提前声明
const tqDbMultiRef = ref(null)
const tqDbListRef = ref(null)
const tqDbSearchRef = ref(null)
Object.assign(tq, {
  conns: [],            // 有效连接（来自连接管理）
  selectedConnId: '',
  databases: [],
  selectedDb: '',
  selectedDbs: [],      // 多选数据库
  dbDropdownOpen: false,
  dbSearch: '',
  tables: {},           // { [db]: string[] }
  tablesLoading: {},    // { [db]: boolean }
  expandedDb: {},       // { [db]: boolean }
  filter: '',
  tableFilters: {},     // { [db]: string } 针对每个库的表名过滤
  tableFilterOpenFor: '', // 当前浮动过滤框打开的库名
  sql: '',
  running: false,
  cancelToken: 0,
  result: null,         // { type: 'table', columns: string[], rows: any[] } | { type: 'text', text: string }
  notices: [],          // { id, text }
  tableColWidths: [],
  bodyScrollX: 0,
  bodyTableWidth: 0,
  // 分页（后端分页）
  page: 1,
  pageSize: 50,
  totalRows: 0,
  pageInput: 1,
  // 直通模式：SQL 含 LIMIT/OFFSET 时由后端直通执行，不进行统一分页
  respectInnerLimit: false
})

// 左侧连接树显隐
if (!('leftCollapsed' in tq)) tq.leftCollapsed = false

// SQL 编辑区默认高度与拖动状态（默认 180 → 130，降低 50px）
// 首次注入高度：与独立页一致 170
if (!('editorHeight' in tq)) tq.editorHeight = 170
let _resizeState = { dragging: false, startY: 0, startHeight: 0 }

// 强制刷新 CodeMirror 视图布局（在容器高度变化后）
function refreshEditorLayout() {
  try {
    if (tqEditorView) {
      // 强制滚动容器占满高度并可滚
      try { tqEditorView.scrollDOM.style.height = '100%'; tqEditorView.scrollDOM.style.overflow = 'auto'; tqEditorView.scrollDOM.style.overflowY = 'auto' } catch {}
      // 触发一次测量，促使视口与滚动区域根据新高度重排
      if (typeof tqEditorView.requestMeasure === 'function') {
        tqEditorView.requestMeasure()
      }
      // 在下一帧再保证一次
      requestAnimationFrame(() => {
        try { if (typeof tqEditorView.requestMeasure === 'function') tqEditorView.requestMeasure() } catch {}
      })
    }
  } catch {}
}

// 结果表格对齐：refs 与列宽同步（JS 版本，无 TS 泛型）
// 注：相关 refs 已在上文提前声明（约 552-555 行），此处复用，避免重复声明

// 向子组件提供 ticket.query 上下文，避免多层 props 传递
try {
  provide('tqCtx', {
    tq,
    // DOM refs（由 ResultTable 挂载后回填，以维持既有逻辑兼容）
    tqEditorRef,
    tqCodeRef,
    tqHeadTableRef,
    tqBodyTableRef,
    tqScrollXRef,
    tqBodyRef,
    // 行为方法
    // Tab 相关
    newQueryTab,
    activateQueryTab,
    closeQueryTab,
    // 编辑器交互
    startResize,
    onSqlHostClick,
    // 表格交互
    headerLockClick,
    toggleSort,
    startColResize,
    onBodyScroll,
    getDisplayedRows,
    computeColWidths,
    adjustHeaderGutter
  })
} catch {}

// 表头与正文水平滚动同步
let _tqSyncingX = false
let _unbindScrollSync = null
let _tqResizeObs = null
function bindTqScrollSync() {
  // 粘性表头方案无需头体水平同步，保持空实现但保留清理逻辑
  unbindTqScrollSync()
}
function unbindTqScrollSync() {
  try { _tqResizeObs && _tqResizeObs.disconnect() } catch {}
  _tqResizeObs = null
  _unbindScrollSync = null
}

// --- 列冻结与拖动：初始化缺省字段 ---
try {
  if (tq.freezeCount === undefined) tq.freezeCount = 0
  if (!Array.isArray(tq.freezeLefts)) tq.freezeLefts = []
} catch {}

// 排序默认值（需在 tq 初始化后执行）
try {
  if (!('sortKey' in tq)) tq.sortKey = ''
  if (!('sortDir' in tq)) tq.sortDir = '' // '', 'asc', 'desc'
} catch {}

async function computeColWidths() {
  await nextTick()
  requestAnimationFrame(() => {
    try {
      if (!tq.result || tq.result.type !== 'table') return
      const bodyTable = tqBodyTableRef.value
      const headTable = tqHeadTableRef.value
      if (!bodyTable) return
      // 使用 offsetWidth 获取像素整数，避免小数取整引起的头体列宽误差
      const getWidths = (cells) => Array.from(cells).map((c) => c && c.offsetWidth ? c.offsetWidth : Math.round(c.getBoundingClientRect().width))
      let widths = []
      const bodyRow = bodyTable && bodyTable.tBodies && bodyTable.tBodies[0] && bodyTable.tBodies[0].rows && bodyTable.tBodies[0].rows[0]
      const headRow = headTable && headTable.tHead && headTable.tHead.rows && headTable.tHead.rows[0]
      if (bodyRow && bodyRow.cells) {
        const wBody = getWidths(bodyRow.cells)
        const wHead = headRow && headRow.cells ? getWidths(headRow.cells) : []
        widths = (tq.result.columns || []).map((_, i) => Math.max(wBody[i] || 0, wHead[i] || 0, 200))
      } else if (headRow && headRow.cells) {
        const wHead = getWidths(headRow.cells)
        widths = (tq.result.columns || []).map((_, i) => Math.max(wHead[i] || 0, 200))
      } else {
        widths = (tq.result.columns || []).map(() => 200)
      }
      if (!widths || widths.length !== (tq.result.columns || []).length) {
        widths = (tq.result.columns || []).map((_, i) => Math.max((widths && widths[i]) || 0, 200))
      }
      // 使用列宽总和作为表总宽（包含边框的实际像素），避免 scrollWidth 与 border 计算差异
      const sumW = (widths || []).reduce((a, b) => a + (b || 0), 0)
      tq.tableColWidths = widths
      tq.bodyTableWidth = sumW || 0
      // 计算冻结列位移
      recomputeFrozenOffsets()
      adjustHeaderGutter()
    } catch (_) { /* noop */ }
  })
}

// 当结果集、分页、排序或冻结数量变化后，在下一帧统一重算列宽与滚动条补偿
watch(
  () => ({
    res: tq.result,
    n: tq.result?.rows?.length,
    cols: tq.result?.columns?.length,
    page: tq.page,
    pageSize: tq.pageSize,
    sortKey: tq.sortKey,
    sortDir: tq.sortDir,
    freeze: tq.freezeCount
  }),
  () => { nextTick().then(() => { computeColWidths(); adjustHeaderGutter() }) },
  { deep: false }
)

// --- 冻结列位移计算 ---
function recomputeFrozenOffsets() {
  try {
    const n = Math.max(0, Math.min(tq.freezeCount || 0, (tq.result?.columns?.length || 0)))
    const lefts = new Array(n).fill(0)
    // 使用列宽累加，避免 sticky 后 offsetLeft 失真
    let acc = 0
    for (let i = 0; i < n; i++) {
      lefts[i] = acc
      acc += (tq.tableColWidths?.[i] || 0)
    }
    tq.freezeLefts = lefts
  } catch {}
}

// --- 列宽拖动 ---
let _resizing = { on: false, col: -1, startX: 0, startW: 0 }
function startColResize(i, e) {
  try {
    if (!Array.isArray(tq.tableColWidths)) return
    _resizing.on = true
    _resizing.col = i
    _resizing.startX = e.clientX
    _resizing.startW = tq.tableColWidths[i] || 200
    document.body.style.userSelect = 'none'
    window.addEventListener('mousemove', onColResizing, { passive: true })
    window.addEventListener('mouseup', stopColResize, { passive: true })
  } catch {}
}
function onColResizing(ev) {
  if (!_resizing.on) return
  const dx = ev.clientX - _resizing.startX
  const next = Math.max(110, _resizing.startW + dx)
  try {
    tq.tableColWidths.splice(_resizing.col, 1, Math.round(next))
    // 同步 colgroup 宽度后，更新冻结位移
    recomputeFrozenOffsets()
  } catch {}
}
function stopColResize() {
  if (!_resizing.on) return
  _resizing.on = false
  _resizing.col = -1
  try { document.body.style.userSelect = '' } catch {}
  try {
    window.removeEventListener('mousemove', onColResizing)
    window.removeEventListener('mouseup', stopColResize)
  } catch {}
}

// --- 导出 CSV ---
function exportCSV() {
  try {
    if (!tq.result || tq.result.type !== 'table') return
    const cols = tq.result.columns || []
    const lines = []
    const esc = (v) => {
      const s = v === null || v === undefined ? '' : String(v)
      return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s
    }
    lines.push(cols.map(esc).join(','))
    for (const row of tq.result.rows || []) {
      lines.push(cols.map((c) => esc(row[c])).join(','))
    }
    const blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'export.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(a.href), 1000)
    pushNotice('CSV 导出完成')
  } catch {}
}

// --- 导出 Excel（优先动态 import，失败再走 CDN/本地，最终回退 CSV） ---
async function exportExcel() {
  try {
    if (!tq.result || tq.result.type !== 'table') return
    pushNotice('正在准备 Excel 导出...')
    const XLSX = await getXLSX()
    if (!XLSX || !XLSX.utils) {
      pushNotice('Excel 组件不可用，已回退为 CSV 导出')
      exportCSV();
      return
    }
    const cols = tq.result.columns || []
    const data = [cols]
    for (const row of (tq.result.rows || [])) data.push(cols.map((c) => row[c]))
    const ws = XLSX.utils.aoa_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
    // 某些浏览器需要显式文件选项
    XLSX.writeFile(wb, 'export.xlsx')
    pushNotice('Excel 导出完成')
  } catch {
    try { pushNotice('Excel 导出失败，已回退 CSV'); exportCSV() } catch {}
  }
}

// --- 简单通知 ---
function pushNotice(text) {
  try {
    const id = Date.now() + Math.random()
    tq.notices = [...(tq.notices || []), { id, text }]
    setTimeout(() => {
      try { tq.notices = (tq.notices || []).filter(n => n.id !== id) } catch {}
    }, 3000)
  } catch {}
}

function adjustHeaderGutter() {
  try {
    const bodyEl = tqBodyRef.value
    const headWrap = tqScrollXRef.value
    if (!bodyEl || !headWrap) return
    const sbw = bodyEl.offsetWidth - bodyEl.clientWidth
    headWrap.style.paddingRight = (sbw > 0 ? sbw : 0) + 'px'
  } catch {}
}

watch(() => tq.result, async (v) => {
  if (v && v.type === 'table') {
    await computeColWidths()
    await nextTick()
    bindTqScrollSync()
  } else {
    unbindTqScrollSync()
  }
  await nextTick()
  try { syncRightHeight() } catch {}
})

function startResize(e) {
  const editorEl = tqEditorRef.value
  const rightEl = tqRightRef.value
  if (!editorEl || !rightEl) return
  try { syncRightHeight() } catch {}
  _resizeState.dragging = true
  _resizeState.startY = e.clientY
  _resizeState.startHeight = editorEl.getBoundingClientRect().height
  try { document.body.style.cursor = 'row-resize'; document.body.classList.add('tq-resizing') } catch {}
  window.addEventListener('mousemove', onResizing)
  window.addEventListener('mouseup', stopResize)
}

function onResizing(e) {
  if (!_resizeState.dragging) return
  const rightEl = tqRightRef.value
  const editorEl = tqEditorRef.value
  const minEditor = 120
  const minResult = 100
  const totalH = rightEl ? rightEl.getBoundingClientRect().height : 0
  const delta = e.clientY - _resizeState.startY
  let next = _resizeState.startHeight + delta
  if (totalH > 0) {
    const maxEditor = Math.max(minEditor, totalH - minResult)
    next = Math.min(Math.max(next, minEditor), maxEditor)
  } else {
    next = Math.max(next, minEditor)
  }
  tq.editorHeight = Math.round(next)
  // 直接写入行内样式与 CSS 变量，确保立刻生效
  try {
    if (editorEl) {
      const px = tq.editorHeight + 'px'
      editorEl.style.height = px
      editorEl.style.flexBasis = px
      editorEl.style.setProperty('--tq-editor-h', px)
      try { console.log('[resize]', { totalH, delta, next: tq.editorHeight, style: { height: editorEl.style.height, flexBasis: editorEl.style.flexBasis } }) } catch {}
      // 同步 CodeMirror 根与滚动容器高度为像素值
      try {
        if (tqEditorView) {
          tqEditorView.dom.style.height = px
          tqEditorView.scrollDOM.style.height = px
        }
      } catch {}
    }
  } catch {}
  // 促使编辑器内部根据新高度立刻重排
  try { refreshEditorLayout() } catch {}
}

function stopResize() {
  if (_resizeState.dragging) {
    _resizeState.dragging = false
    window.removeEventListener('mousemove', onResizing)
    window.removeEventListener('mouseup', stopResize)
    try { document.body.style.cursor = ''; document.body.classList.remove('tq-resizing') } catch {}
    // 结束拖拽后再强制刷新一次布局
    try {
      const px = tq.editorHeight + 'px'
      if (tqEditorView) {
        tqEditorView.dom.style.height = px
        tqEditorView.scrollDOM.style.height = px
      }
      refreshEditorLayout()
    } catch {}
  }
}

function addNotice(text, ttlMs = 3000) {
  const id = Date.now() + Math.random()
  tq.notices.push({ id, text })
  setTimeout(() => {
    const i = tq.notices.findIndex(n => n.id === id)
    if (i !== -1) tq.notices.splice(i, 1)
  }, ttlMs)
}

async function ensureTicketInit() {
  if (tq._inited) return
  tq._inited = true
  await loadConnsFromModule()
  await nextTick()
  updateTqMainHeight()
}

async function loadConnsFromModule() {
  // 从连接管理模块的列表中拿有效连接（status==='1'）
  try {
    if (!Array.isArray(list.value) || list.value.length === 0) {
      // 若还未加载过，调用连接管理的查询
      await fetchList()
    }
  } catch {}
  const rows = Array.isArray(list.value) ? list.value : []
  tq.conns = rows.filter(it => String(it.status) === '1')
  if (!tq.conns.find(c => c.id === tq.selectedConnId)) {
    tq.selectedConnId = ''
  }
}

async function onConnChange() {
  tq.selectedDb = ''
  tq.selectedDbs = []
  tq.dbSearch = ''
  tq.dbDropdownOpen = false
  tq.forceTreeFilter = false
  tq.databases = []
  tq.tables = {}
  tq.expandedDb = {}
  if (!tq.selectedConnId) return
  try {
    const params = { connId: tq.selectedConnId, connectionId: tq.selectedConnId, conn_id: tq.selectedConnId, id: tq.selectedConnId }
    console.debug('[ticket.query] load databases', params)
    const { data } = await getWithFallback([
      `/ticket/databases`,
      `/connections/${tq.selectedConnId}/databases`,
    ], { params })
    console.debug('[ticket.query] databases resp', data)
    tq.databases = Array.isArray(data) ? data : []
    // 不再自动选择或展开数据库；由用户手动选择/展开
  } catch (e) {
    console.error('[ticket.query] 加载数据库失败', e)
    const msg = e?.response?.data?.message || e?.response?.data?.detail || e?.message || '加载数据库失败'
    addNotice(`加载数据库失败：${msg}`)
  }
  await nextTick(); updateTqMainHeight()
}

async function onDbChange() {
  if (!tq.selectedDb) return
  await loadTables(tq.selectedDb)
}

// 数据库多选与搜索
const filteredDatabases = computed(() => {
  const kw = (tq.dbSearch || '').toLowerCase().trim()
  const arr = Array.isArray(tq.databases) ? tq.databases : []
  if (!kw) return arr
  return arr.filter(d => String(d).toLowerCase().includes(kw))
})

function toggleDbDropdown() {
  if (!tq.selectedConnId) return
  tq.dbDropdownOpen = !tq.dbDropdownOpen
  // 选中库数>=1 时，无论面板是否打开都保持树过滤
  tq.forceTreeFilter = !!(Array.isArray(tq.selectedDbs) && tq.selectedDbs.length >= 1)
  if (tq.dbDropdownOpen) {
    nextTick(() => {
      try { if (tqDbListRef.value) tqDbListRef.value.scrollTop = 0 } catch {}
      try { if (tqDbSearchRef.value) tqDbSearchRef.value.focus() } catch {}
    })
  }
}

function onDbToggle(db, evt) {
  const checked = !!evt?.target?.checked
  const i = tq.selectedDbs.indexOf(db)
  if (checked) {
    if (i < 0) tq.selectedDbs.push(db)
  } else {
    if (i >= 0) tq.selectedDbs.splice(i, 1)
  }
  // 当下拉面板打开时，根据多选数量动态控制左侧树是否过滤
  // 选中库数>=1 时，无论面板是否打开都保持树过滤
  tq.forceTreeFilter = !!(tq.selectedDbs.length >= 1)
}

// 强同步：
// 1) 活动库 = 多选第一项；
// 2) 多选(>1)时不自动展开二级菜单；单选时自动展开该库；
// 3) 为选中库按需加载表；取消选中的库自动折叠。
watch(() => (tq.selectedDbs || []).slice(), (arr, oldArr) => {
  try {
    const next = Array.isArray(arr) ? arr : []
    const prev = Array.isArray(oldArr) ? oldArr : []
    const isMulti = next.length > 1
    // 选中库数>=1 时，保持树过滤
    tq.forceTreeFilter = next.length >= 1

    // 1) 活动库强同步
    const first = next.length ? next[0] : ''
    if (first !== tq.selectedDb) {
      tq.selectedDb = first || ''
    }

    // 2) 计算增量与减量
    const nextSet = new Set(next)
    const prevSet = new Set(prev)
    const added = next.filter(d => !prevSet.has(d))
    const removed = prev.filter(d => !nextSet.has(d))

    // 3) 二级菜单展开策略
    if (isMulti) {
      // 多选：不自动展开任何库
      for (const k in tq.expandedDb) {
        tq.expandedDb[k] = false
      }
    } else {
      // 单选：自动展开该库
      if (first) {
        tq.expandedDb[first] = true
      }
    }

    // 4) 为已选中的库确保加载表（是否展开不影响）
    for (const db of next) {
      if (!tq.tables[db] && !tq.tablesLoading?.[db]) {
        loadTables(db)
      }
    }

    // 5) 对取消选择库：折叠（不清空数据，避免重复加载）
    for (const db of removed) {
      if (tq.expandedDb && db in tq.expandedDb) {
        tq.expandedDb[db] = false
      }
    }
  } catch {}
}, { deep: false })

// 首次挂载时做一次初始同步，防止进入页面前已存在多选但未触发 watcher 的情况
onMounted(() => {
  try {
    const next = Array.isArray(tq.selectedDbs) ? tq.selectedDbs.slice() : []
    // 活动库
    tq.selectedDb = next.length ? next[0] : ''
    // 展开与加载：多选不展开；单选自动展开；均按需加载表
    if (next.length > 1) {
      for (const k in tq.expandedDb) tq.expandedDb[k] = false
    } else if (next.length === 1) {
      const first = next[0]
      tq.expandedDb[first] = true
    }
    for (const db of next) {
      if (!tq.tables[db] && !tq.tablesLoading?.[db]) {
        loadTables(db)
      }
    }
  } catch {}
})

function confirmDbSelection() {
  tq.dbDropdownOpen = false
  // 若尚未设置活动数据库，则默认取第一个
  if (!tq.selectedDb && tq.selectedDbs.length) {
    tq.selectedDb = tq.selectedDbs[0]
    onDbChange()
  }
}

function clearDbSelection() {
  tq.selectedDbs = []
  tq.selectedDb = ''
  tq.dbSearch = ''
  // 保持列表面板不关闭，并复位滚动与焦点
  tq.forceTreeFilter = false
  nextTick(() => {
    try { if (tqDbListRef.value) tqDbListRef.value.scrollTop = 0 } catch {}
    try { if (tqDbSearchRef.value) tqDbSearchRef.value.focus() } catch {}
  })
}

async function loadTables(db) {
  if (!db || !tq.selectedConnId) return
  tq.tablesLoading[db] = true
  try {
    const params = { connId: tq.selectedConnId, connectionId: tq.selectedConnId, conn_id: tq.selectedConnId, id: tq.selectedConnId, db, database: db, schema: db }
    console.debug('[ticket.query] load tables', params)
    const { data } = await getWithFallback([
      `/ticket/tables`,
      `/connections/${tq.selectedConnId}/tables`,
    ], { params })
    console.debug('[ticket.query] tables resp', db, data)
    tq.tables[db] = Array.isArray(data) ? data : []
  } catch (e) {
    console.error(`[ticket.query] 加载 ${db} 表失败`, e)
    const msg = e?.response?.data?.message || e?.response?.data?.detail || e?.message || `加载 ${db} 表失败`
    addNotice(`加载 ${db} 表失败：${msg}`)
  } finally {
    tq.tablesLoading[db] = false
  }
}

function toggleDbExpand(db) {
  tq.expandedDb[db] = !tq.expandedDb[db]
  if (tq.expandedDb[db]) {
    // 同步上方下拉框选中库
    tq.selectedDb = db
    // 首次展开时加载表
    if (!tq.tables[db] && !tq.tablesLoading[db]) {
      loadTables(db)
    }
  }
}

function filteredTables(db) {
  const arr = tq.tables[db] || []
  const f = (tq.tableFilters?.[db] || '').toLowerCase().trim()
  if (!f) return arr
  return arr.filter(x => String(x).toLowerCase().includes(f))
}

async function appendTableToSQL(db, tbl) {
  try { console.log('[ticket.query] appendTableToSQL click', { db, tbl, hasEditor: !!tqEditorView }) } catch {}
  const snippet = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;\n`

  // 确保编辑器已初始化（等待）
  if (!tqEditorView) {
    try { await ensureSqlEditor() } catch {}
  }

  if (tqEditorView) {
    try {
      const doc = tqEditorView.state.doc.toString()
      const prefix = doc && !/\n$/.test(doc) ? '\n' : ''
      const insert = prefix + snippet
      tqEditorView.dispatch({
        changes: { from: tqEditorView.state.doc.length, to: tqEditorView.state.doc.length, insert }
      })
      try { console.log('[ticket.query] appendTableToSQL inserted into editor') } catch {}
      tqEditorView.focus()
      return
    } catch {}
  }

  // 兜底：仍未创建成功则直接追加到 tq.sql
  const prefix = tq.sql && !/\n$/.test(tq.sql) ? '\n' : ''
  tq.sql += prefix + snippet
  try { console.log('[ticket.query] appendTableToSQL appended to tq.sql, editor missing') } catch {}
}

async function executeSQL() {
  if (!tq.sql.trim()) return
  tq.running = true
  tq.cancelToken = Date.now()
  const myToken = tq.cancelToken
  tq.result = { type: 'text', text: '执行中...' }
  try {
    const hasInnerLimit = /\blimit\b/i.test(tq.sql)
    tq.respectInnerLimit = !!hasInnerLimit
    try { console.debug('[ticket.query] executeSQL send', { page: tq.page, pageSize: tq.pageSize, respectInnerLimit: hasInnerLimit }) } catch {}
    const { data } = await api.post('/ticket/execute', {
      connId: tq.selectedConnId,
      database: tq.selectedDb,
      sql: tq.sql,
      page: tq.page,
      pageSize: tq.pageSize,
      respectInnerLimit: hasInnerLimit
    })
    if (tq.cancelToken !== myToken) return
    if (data && Array.isArray(data.rows) && Array.isArray(data.columns)) {
      tq.result = { type: 'table', columns: data.columns, rows: data.rows }
      // 兼容不同字段名：total/totalRows/count；当未提供时回退为当前返回行数
      const totRaw = (data.total !== undefined ? data.total : (data.totalRows !== undefined ? data.totalRows : data.count))
      const tot = Number(totRaw)
      tq.totalRows = (Number.isFinite(tot) && tot >= 0) ? tot : (Array.isArray(data.rows) ? data.rows.length : 0)
      try {
        const cols = Array.isArray(data.columns) ? data.columns : []
        const idKey = cols.includes('id') ? 'id' : (cols[0] || null)
        const firstId = (Array.isArray(data.rows) && data.rows.length) ? (data.rows[0]?.[idKey] ?? data.rows[0]?.[0]) : undefined
        const lastId = (Array.isArray(data.rows) && data.rows.length) ? (data.rows[data.rows.length-1]?.[idKey] ?? data.rows[data.rows.length-1]?.[0]) : undefined
        console.debug('[ticket.query] executeSQL resp', { pageEcho: data.pageEcho, pageSizeEcho: data.pageSizeEcho, totalRows: tq.totalRows, rows: data.rows?.length, firstId, lastId })
      } catch {}
    } else if (typeof data === 'string') {
      tq.result = { type: 'text', text: data }
    } else if (data && data.message) {
      tq.result = { type: 'text', text: data.message }
    } else {
      tq.result = { type: 'text', text: '执行完成' }
    }
    addNotice('执行完成')
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '执行失败'
    tq.result = { type: 'text', text: String(msg) }
    try { console.error('[ticket.query] executeSQL error', e?.response?.data || e) } catch {}
    addNotice('执行失败')
  } finally {
    if (tq.cancelToken === myToken) tq.running = false
  }
}

// 分页控制（后端分页：跳页即查询该页）
const tqTotalPages = computed(() => {
  // 直通模式下强制视为 1 页，避免误导
  if (tq.respectInnerLimit) return 1
  return Math.max(1, Math.ceil((tq.totalRows || 0) / (tq.pageSize || 50)))
})
function goToPage(n) {
  if (tq.respectInnerLimit) return // 直通模式不响应分页
  const tp = tqTotalPages.value
  const target = Math.min(Math.max(1, Number(n) || 1), tp)
  if (target === tq.page) return
  tq.page = target
  executeSQL()
}

// 同步输入框与当前页
watch(() => tq.page, (v) => { tq.pageInput = v })

function stopExecution() {
  // 简单的前端取消标记；后端可扩展真正的取消
  tq.cancelToken = 0
  tq.running = false
  addNotice('已请求停止')
}

function beautifySQL() {
  // 轻量美化：去除多余空白，分号后换行
  if (!tq.sql) return
  let s = tq.sql
  s = s.replace(/[\t ]+/g, ' ').replace(/\s*;\s*/g, ';\n').replace(/\n{3,}/g, '\n\n').trim() + '\n'
  tq.sql = s
}

async function viewPlan() {
  if (!tq.sql.trim()) return
  try {
    const { data } = await api.post('/ticket/plan', {
      connId: tq.selectedConnId,
      database: tq.selectedDb,
      sql: tq.sql,
    })
    if (typeof data === 'string') {
      tq.result = { type: 'text', text: data }
    } else if (data && data.message) {
      tq.result = { type: 'text', text: data.message }
    } else {
      tq.result = { type: 'text', text: JSON.stringify(data, null, 2) }
    }
    addNotice('计划生成完成')
  } catch (e) {
    tq.result = { type: 'text', text: e?.response?.data?.detail || e.message || '获取执行计划失败' }
    addNotice('获取执行计划失败')
  }
}

// 当切换到工单查询时初始化
watch(activeTab, async (v) => {
  if (v === 'ticket.query') {
    await ensureTicketInit()
    await nextTick(); updateTqMainHeight()
  }
})

function updateTqMainHeight() {
  const container = tqContainerRef.value
  const el = tqMainRef.value
  if (!el) return
  // 将 .tq-main 拉伸至贴合视口底部（保留 0px 空隙）
  const rect = el.getBoundingClientRect()
  const viewH = window.innerHeight || document.documentElement.clientHeight
  let target = Math.max(420, viewH - rect.top)
  el.style.boxSizing = 'border-box'
  el.style.height = target + 'px'
  el.style.marginBottom = '0'
  // 二次校正，确保真实间隙≈0px
  requestAnimationFrame(() => {
    const after = el.getBoundingClientRect()
    const gap = Math.round(viewH - after.bottom)
    const delta = gap - 0
    if (Math.abs(delta) > 1) {
      const adjusted = Math.max(420, target + delta)
      el.style.height = adjusted + 'px'
    }
  })
  if (container) {
    container.style.paddingBottom = '0'
    container.style.marginBottom = '0'
  }
}

function handleResizeOrScroll() { updateTqMainHeight() }

onMounted(() => {
  window.addEventListener('resize', handleResizeOrScroll)
  window.addEventListener('scroll', handleResizeOrScroll, { passive: true })
  if (previewRef.value) {
    previewRef.value.addEventListener('scroll', handleResizeOrScroll, { passive: true })
  }
  // 防止拖拽时选中文本
  window.addEventListener('mouseleave', stopResize)
  // 初始也尝试一次
  setTimeout(updateTqMainHeight, 0)
  // 首次与窗口变化时，同步列宽，避免尺寸变化导致错位
  window.addEventListener('resize', computeColWidths)
  window.addEventListener('resize', adjustHeaderGutter)
  computeColWidths()
  // 水平滚动同步：以表头滚动为主，正文仅做视觉位移
  const headWrap = tqScrollXRef.value
  if (headWrap) {
    headWrap.addEventListener('scroll', () => {
      const x = headWrap.scrollLeft
      try {
        const body = tqBodyRef.value
        if (body && body.scrollLeft !== x) body.scrollLeft = x
      } catch {}
      tq.bodyScrollX = x
    }, { passive: true })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResizeOrScroll)
  window.removeEventListener('scroll', handleResizeOrScroll)
  window.removeEventListener('mouseleave', stopResize)
  if (previewRef.value) {
    previewRef.value.removeEventListener('scroll', handleResizeOrScroll)
  }
  window.removeEventListener('resize', computeColWidths)
  window.removeEventListener('resize', adjustHeaderGutter)
  // 解除表头/正文滚动同步
  try { unbindTqScrollSync() } catch {}
})

const totalPages = computed(() => Math.max(1, Math.ceil((filteredList?.value?.length || 0) / pageSize.value)))
const pagedList = computed(() => {
  const arr = filteredList?.value || []
  const start = (page.value - 1) * pageSize.value
  return arr.slice(start, start + pageSize.value)
})
function prevPage() { if (page.value > 1) page.value-- }
function nextPage() { if (page.value < totalPages.value) page.value++ }

// 字典数据
const dictType = ref([])   // 01 数据源类型
const dictEnv = ref([])    // 02 数据库环境
const dictStatus = ref([]) // 03 数据源状态

const form = reactive({
  ip: '',
  port: '',
  user: '',
  password: '',
  db_type: '',
  db_env: '',
  status: '1',
  description: ''
})

function resetForm() {
  editing.value = false
  editingId.value = null
  form.ip = ''
  form.port = ''
  form.user = ''
  form.password = ''
  form.db_type = ''
  form.db_env = ''
  form.status = '1'
  form.description = ''
}

function onCreateNew() {
  // 清空除状态以外的所有字段，并确保表单全新渲染
  resetForm()
  message.value = ''
  // 通过变更 key 强制重建输入控件，避免浏览器残留自动填充
  formKey.value++
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  resetForm()
}

function setActive(key) {
  activeMenu.value = key
  // 切换到连接管理时默认查询
  if (key === 'conn') {
    fetchList()
  }
}

const activeTitle = computed(() => {
  const map = {
    'ticket.platform': '工单平台',
    'ticket.query': '工单平台 - 工单查询',
    'ticket.publish': '工单平台 - 工单发布',
    'ticket.review': '工单平台 - 工单审核',
    'ticket.run': '工单平台 - 工单运行',
    'report.platform': '报表平台',
    'screen.mgmt': '大屏管理',
    'report.task': '报表任务',
    'user.mgmt': '用户管理',
    'role.mgmt': '角色管理',
    'sys.settings': '系统设置',
  }
  return map[activeMenu.value] || '预览'
})

async function fetchList() {
  try {
    const { data } = await api.get('/connections')
    list.value = data
    page.value = 1
  } catch (e) {
    message.value = '加载失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onQuery() {
  fetchList()
}

async function fetchDicts() {
  try {
    const [t, e, s] = await Promise.all([
      api.get('/dicts/01'),
      api.get('/dicts/02'),
      api.get('/dicts/03'),
    ])
    dictType.value = t.data
    dictEnv.value = e.data
    dictStatus.value = s.data
  } catch (err) {
    message.value = '加载字典失败: ' + (err?.response?.data?.detail || err.message)
  }
}

function labelOf(arrRef, value) {
  const arr = Array.isArray(arrRef) ? arrRef : arrRef?.value
  const f = (arr || []).find(i => i.dmm === (value ?? ''))
  return f?.dmmc || value || ''
}

async function onSubmit() {
  try {
    // 前端必填校验（中文提示）
    if (!form.ip) return (message.value = '请填写数据库IP')
    if (!form.port) return (message.value = '请填写数据库端口')
    if (!form.user) return (message.value = '请填写用户名')
    if (!editing.value && !form.password) return (message.value = '请填写密码')
    if (!form.db_type) return (message.value = '请选择类型')
    if (!form.db_env) return (message.value = '请选择环境')
    if (!form.status) return (message.value = '请选择状态')

    if (editing.value && editingId.value) {
      const payload = { ...form }
      // 编辑场景：只有在输入了新密码时才更新密码；留空则不修改
      if (!payload.password || String(payload.password).trim() === '') {
        delete payload.password
      }
      const { data } = await api.put(`/connections/${editingId.value}`, payload)
      message.value = `已保存 #${data.id}`
    } else {
      const { data } = await api.post('/connections', { ...form })
      message.value = `已创建 #${data.id}`
    }
    await fetchList()
    closeModal()
  } catch (e) {
    message.value = '提交失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onEdit(item) {
  editing.value = true
  editingId.value = item.id
  form.ip = item.ip
  form.port = item.port
  form.user = item.user
  form.password = ''
  form.db_type = item.db_type || ''
  form.db_env = item.db_env || ''
  form.status = item.status || '1'
  form.description = item.description || ''
  showModal.value = true
}

function onDelete(item) {
  confirmItem.value = item
  const fallback = `${item.ip}:${item.port} (#${item.id})`
  const label = (item.description && item.description.trim()) ? item.description.trim() : fallback
  confirmText.value = `确定要删除 “${label}” 吗？`
  confirmVisible.value = true
}

function cancelConfirm() {
  confirmVisible.value = false
  confirmItem.value = null
  confirmText.value = ''
}

async function performDelete() {
  const item = confirmItem.value
  if (!item) return cancelConfirm()
  try {
    await api.delete(`/connections/${item.id}`)
    message.value = `已删除 #${item.id}`
    await fetchList()
  } catch (e) {
    message.value = '删除失败: ' + (e?.response?.data?.detail || e.message)
  } finally {
    cancelConfirm()
  }
}

async function onTest(item) {
  try {
    const { data } = await api.post(`/connections/${item.id}/test`)
    message.value = `测试结果: ${data.success ? '成功' : '失败'}`
  } catch (e) {
    message.value = '测试失败: ' + (e?.response?.data?.detail || e.message)
  }
}

onMounted(async () => {
  await fetchDicts()
  // 连接管理默认查询一次
  await fetchList()
  // 强制清空一次，覆盖浏览器自动填充
  resetForm()
  // 触发一次表单重渲染，进一步清理 autofill
  formKey.value++
  // 在下一次 DOM 更新后再次清空，避免密码管理器晚注入
  await nextTick()
  resetForm()
  formKey.value++
  // 再加一次延时清理，兼容部分浏览器延迟填充
  setTimeout(() => {
    resetForm()
    formKey.value = 1
  }, 300)
  
  // 原有的事件监听
  window.addEventListener('beforeunload', () => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.close()
    }
  })
  
  // 监听来自连接管理的"打开控制台"事件
  try {
    window.addEventListener('open-console', (event) => {
      const id = event.detail?.connId
      if (!id) return
      openConsole(id)
    })
  } catch {}
  
  // 监听来自连接管理的“打开控制台”事件
  try {
    window.addEventListener('dv:open-console', (ev) => {
      const id = ev?.detail?.connId
      if (!id) return
      openConsole(id)
    })
  } catch {}

  // 监听来自独立 SQL 页的 postMessage，请求在主页面打开浮动控制台
  try {
    window.addEventListener('message', async (ev) => {
      try {
        // 仅处理同源消息
        if (ev.origin !== window.location.origin) return
        const data = ev.data || {}
        if (data && data.type === 'open-sql-modal') {
          const payload = data.payload || {}
          const connId = payload.connId
          const database = payload.database
          const sql = payload.sql
          if (connId) {
            await openConsole(connId)
          } else {
            // 没有 connId 则仅确保浮动控制台可见
            await openConsole(tq?.selectedConnId || consoleModal.connId)
          }
          // 一次性应用数据库与 SQL（如有）
          try { if (database) tq.selectedDb = database } catch {}
          try {
            if (sql) {
              tq.sql = sql
              // 若编辑器存在，强制更新一次内容
              try {
                if (typeof window.__tqEnsure === 'function') window.__tqEnsure()
                const v = window && window.__tqEditorView
                if (v && v.state) {
                  const cur = v.state.doc.toString()
                  if (cur !== sql) v.dispatch({ changes: { from: 0, to: cur.length, insert: sql } })
                }
              } catch {}
            }
          } catch {}
        }
      } catch {}
    })
  } catch {}
})

const filteredList = computed(() => {
  return list.value.filter(it => {
    if (filter.type && it.db_type !== filter.type) return false
    if (filter.env && it.db_env !== filter.env) return false
    if (filter.status && it.status !== filter.status) return false
    return true
  })
})

</script>

<style scoped>
/* 使用变量管理侧栏宽度，折叠为 0 完全隐藏 */
.app-layout { --sidebar-w: 200px; --content-pad-left: 16px; display: grid; grid-template-columns: var(--sidebar-w) 1fr; height: 100vh; transition: grid-template-columns .2s ease; }
.app-layout.collapsed { --sidebar-w: 0px; grid-template-columns: 0 1fr; }

/* 侧栏采用 flex 布局，滚动交给 nav 区域 */
.sidebar { position: relative; border-right: 1px solid var(--sidebar-border, #e4e8f5); padding: 16px 16px 16px 20px; background: var(--sidebar-bg, linear-gradient(180deg, #f5f8ff 0%, #eef4ff 100%)); box-shadow: 2px 0 8px rgba(0,0,0,0.04); overflow: hidden; display: flex; flex-direction: column; }
.sidebar nav { flex: 1; overflow: auto; }
.app-layout.collapsed .brand-name { display: none; }
/* 折叠时彻底隐藏侧栏本体，避免残留细线或空隙 */
.app-layout.collapsed .sidebar { display: none; border: 0; padding: 0; box-shadow: none; }

/* 侧栏拖拽条 */
.app-layout { --sidebar-w: 200px; position: relative; display: grid; grid-template-columns: var(--sidebar-w) 1fr; height: 100vh; transition: grid-template-columns .2s ease; }
.sidebar-resizer { position: absolute; top: 0; left: var(--sidebar-w); width: 2px; height: 100%; cursor: col-resize; z-index: 120; background: transparent; }
.sidebar-resizer::after { content: ""; position: absolute; top: 0; bottom: 0; left: 0; width: 1px; background: rgba(0,0,0,0.06); }
/* 隐藏旧的折叠按钮 */
.toggle-btn { display: none !important; }

/* 预览区在任何状态都保持可见并占满可用空间 */
.app-layout main.preview { display: block; min-width: 0; min-height: 0; grid-column: 2; grid-row: 1; overflow: auto; -webkit-overflow-scrolling: touch; padding-bottom: 0; margin-bottom: 0; }
.app-layout.collapsed main.preview { display: block !important; min-width: 0; }
/* 小屏自适应：隐藏侧栏、预览区铺满全宽 */
@media (max-width: 768px) {
  .app-layout { grid-template-columns: 1fr !important; }
  .app-layout .sidebar { display: none !important; }
  .app-layout main.preview { grid-column: 1 !important; grid-row: 1; }
  .toggle-btn { left: 8px !important; }
}

/* 预览区内的表格：不换行，超出时走横向滚动 */
.app-layout main.preview :deep(table) { width: max-content; table-layout: auto; }
.app-layout main.preview :deep(th),
.app-layout main.preview :deep(td) { white-space: nowrap; }
.app-layout main.preview { overflow-x: auto; overflow-y: hidden; }

/* 模态窗口样式 */
.dv-modal { position: fixed; inset: 0; z-index: 1000; }
.dv-modal-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.4); }
.dv-modal-panel { position: fixed; inset: 0; width: 100vw; height: 100vh; background: #fff; border-radius: 0; box-shadow: none; display: flex; flex-direction: column; overflow: auto; padding-bottom: 16px; }
.dv-modal-header { position: relative; padding: 12px 56px 12px 16px; border-bottom: 1px solid #eee; }
.dv-modal-header .console-conn-info { margin-left: 6px; font-size: 13px; color: #64748b; font-weight: 500; }
.modal-back-btn { position: absolute; top: 6px; right: 14px; border: none; background: transparent; color: #0b57d0; font-size: 18px; line-height: 1; cursor: pointer; padding: 6px; border-radius: 6px; }
.modal-back-btn:hover { background: #eef2ff; color: #063e99; }

.brand { display:flex; align-items:center; gap:8px; font-weight: 800; margin-bottom: 12px; font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; letter-spacing: .3px; color:#0b57d0; }
.brand-logo { width: 28px; height: 28px; object-fit: contain; }
.brand-name { font-size: 14px; font-weight: 700; }
/* 恢复菜单区原样式 */
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar li { display:block; padding: 8px 12px; border-radius: 10px; cursor: pointer; font-size: 14px; color: #1e40af; box-sizing: border-box; margin: 0; font-weight: 500; letter-spacing: .1px; }
.sidebar li > .mi { width: 18px; height: 18px; margin-right: 8px; display:inline-flex; align-items:center; justify-content:center; vertical-align: middle; color: inherit; opacity: .9; }
.sidebar li > .mi svg { width: 18px; height: 18px; fill: currentColor; color: inherit; }
.sidebar li.group { display:block; padding: 0; }
/* 菜单从上到下展示，水平居中 */
.sidebar { display: flex; flex-direction: column; align-items: stretch; }
.sidebar nav { flex: 1; display: flex; flex-direction: column; width: 100%; }
.sidebar nav > ul { margin-top: 0; margin-bottom: 0; display: flex; flex-direction: column; align-items: stretch; gap: 6px; }
.sidebar li { width: 100%; text-align: left; transition: background .15s ease, color .15s ease; }
/* 悬停：文字与图标略提亮，背景更浅，避免描边和左侧竖线 */
.sidebar li:hover { background: rgba(255,255,255,.55) !important; color: #0b57d0; }
.sidebar li:hover > .mi { opacity: 1; }
/* 选中：白底卡片 + 主色文字，适配浅色渐变背景，不加边框 */
.sidebar li.active { background: rgba(255,255,255,.9) !important; color: #0b57d0 !important; font-weight: 450; }
.sidebar li.active > .mi { opacity: 1; }
/* 侧栏菜单项：移除悬停/聚焦时的矩形描边与左侧粗竖线 */
.sidebar li,
.sidebar li * { outline: none !important; }
.sidebar li { border: none !important; border-left: none !important; box-shadow: none !important; }
.sidebar li:hover,
.sidebar li:focus,
.sidebar li:focus-visible,
.sidebar li:active { border: none !important; border-left: none !important; outline: none !important; box-shadow: none !important; }
.sidebar li::before,
.sidebar li::after { display: none !important; content: none !important; }
.sidebar li.active { border: none !important; box-shadow: none !important; }
/* 侧栏展开菜单：去掉周边边框/投影，保持干净 */
.sidebar li.group { border: none !important; box-shadow: none !important; background: transparent !important; }
.sidebar .group .group-title { border: none !important; box-shadow: none !important; background: transparent !important; color: #1e40af; font-weight: 450; }
.sidebar .group .sub { list-style: none; margin: 4px 0 0 28px; padding: 6px 0; border: none !important; box-shadow: none !important; background: transparent !important; }
.sidebar .group .sub li { border: none !important; box-shadow: none !important; background: transparent !important; padding-left: 0; color: #1f3b8a; font-size: 13.5px; border-radius: 8px; }
.sidebar .group .sub li:hover { background: rgba(255,255,255,.5) !important; color: #0b57d0; }
.sidebar .group .sub li.active { background: rgba(255,255,255,.85) !important; border: none !important; color: #0b57d0; font-weight: 450; }
/* 去掉展开分组左侧的竖线（可能由边框或伪元素绘制） */
.sidebar .group, .sidebar .group * { outline: none !important; }
.sidebar .group, .sidebar .group .sub { border-left: none !important; }
.sidebar .group::before,
.sidebar .group::after,
.sidebar .group .sub::before,
.sidebar .group .sub::after,
.sidebar .group .sub li::before,
.sidebar .group .sub li::after { display: none !important; content: none !important; }
.sidebar .group .sub li { border-left: none !important; position: relative; }
/* 预览区顶部信息栏 */
.top-info { display: grid; grid-template-columns: 1fr 1.5fr auto; gap: 12px; align-items: center; padding: 10px 12px; background: #f7f9fc; border: 1px solid #e5eaf2; border-radius: 10px; margin-bottom: 10px; }
.top-info .datetime { font-weight: 400; color: #0b57d0; white-space: nowrap; font-size: 14px; }
.top-info .lunar { color: #0b57d0; margin-left: 8px; font-size: 14px; }
.top-info .weather { color: #0b57d0; white-space: nowrap; font-size: 14px; }
.top-info .advice { color: #0b57d0; font-size: 14px; }
.top-info .info-center { color: #0b57d0; display: flex; align-items: center; gap: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.top-info .info-center .weather, .top-info .info-center .advice { white-space: inherit; }
.top-info .avatar { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #d0d7de; box-shadow: 0 1px 3px rgba(0,0,0,0.08); background:#fff; object-fit: contain; }
/* 标签栏 */
.tabs-bar { position: relative; display: flex; align-items: center; gap: 6px; padding: 6px 6px 0; background: transparent; border-bottom: 1px solid #e5e7eb; margin-bottom: 8px; overflow: visible; }
/* 彻底禁用 Chrome 风格辅助线与伪元素 */
.tabs-bar::before, .tabs-bar::after, .tabs-seam-hline { display: none !important; content: none !important; }
/* Chrome 风格：略带弧度的顶部圆角、活动项抬起且覆盖底部分隔线 */
.tab-item { position: relative; display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; padding-right: 24px; background: #f3f4f6; border: 1px solid #e5e7eb; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; cursor: pointer; color: #0b57d0; font-size: 14px; font-weight: 400; }
/* 相邻标签无间隙，使用左边框形成连续分隔线（Chrome 风格） */
.tab-item + .tab-item { margin-left: 0; }
.tab-item:hover { background: #e6ebff; }
.tab-item.active { background: #ffffff; color: #0b57d0; border-color: #c7d2fe; z-index: 2; box-shadow: none; }
.tab-title { display: block; max-width: 220px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }
/* 左右两侧过渡：用伪元素把外边缘与标签栏底色平滑连接，形成 Chrome 弧形缝隙效果 */
/* 去除所有伪元素弧形与辅助线 */
.tab-item::before, .tab-item::after { display: none; content: none; }
/* 关闭按钮：仅在悬停或激活时清晰可见，圆形，靠右上角 */
.tab-close {
  position: absolute; top: 4px; right: 6px;
  width: 18px; height: 18px; border-radius: 50%;
  font-size: 12px; line-height: 18px; text-align: center;
  display: inline-flex; align-items: center; justify-content: center;
  color: #475569; background: transparent; border: none;
  opacity: .0; transition: background .15s ease, opacity .15s ease;
  pointer-events: auto;
}
.tab-item:hover .tab-close, .tab-item.active .tab-close { opacity: .9; }
.tab-close:hover { background: #e5e7eb; }
.sidebar li.active { background: #eef4ff; color: #0b57d0; }
.sidebar li:hover { background: #f3f3f3; }
.sidebar .group .group-title { display:block; width: 100%; box-sizing: border-box; margin: 0; padding: 8px 12px; border-radius: 6px; cursor: pointer; }
.sidebar .group .group-title { display:flex; align-items:center; justify-content: space-between; }
.sidebar .group .group-title .mi-wrap { display: inline-flex; align-items: center; gap: 8px; }
.sidebar .group .group-title .mi { width: 18px; height: 18px; display:inline-flex; align-items:center; justify-content:center; }
.sidebar .group .group-title .mi svg { width: 18px; height: 18px; }
.sidebar .group .group-title .arrow { margin-left: 8px; }
.sidebar .group .group-title:hover { background:#f3f3f3; }
.sidebar .group .sub { margin-left: 12px; margin-top: 4px; }
.sidebar .group .sub li { padding-left: 36px; }
.sidebar .arrow { transition: transform .2s ease; display:inline-block; transform: rotate(90deg); }
.sidebar .arrow.open { transform: rotate(270deg); }
.preview { overflow: auto; }
.container { width: 100%; max-width: none; margin: 16px 0; padding: 0 0; }
.preview { padding: 0 var(--content-pad-left) 0 var(--content-pad-left) !important; }
.app-layout.collapsed .preview { padding: 0 var(--content-pad-left) 0 var(--content-pad-left) !important; }
h1 { margin-bottom: 16px; }
.form-section { margin-bottom: 24px; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.grid .span-2 { grid-column: span 2; }
label { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
input, select { padding: 8px 10px; border: 1px solid #dcdcdc; border-radius: 6px; }
.actions { margin-top: 12px; display: flex; gap: 8px; }
button { padding: 6px 10px; border: 1px solid #c9c9c9; border-radius: 6px; background: #fff; cursor: pointer; }
button.primary { border-color: #3b82f6; color: #0b57d0; }

/* ================= 工单查询布局与滚动（左树/右编辑器） ================= */
/* 主区卡片：两列布局（左树 + 右侧），高度由 JS 同步为贴底；此处仅保证内部 100% 占满 */
.ticket-query .tq-main { position: relative; display: grid; grid-template-rows: 1fr; gap: 0; height: 100%; min-height: 420px; overflow: hidden; }
/* 左侧树容器：占满父容器高度并开启垂直滚动，避免滚动条消失 */
.ticket-query .tq-left { min-width: 0; height: 100%; padding-right: 6px; box-sizing: border-box; border-right: 1px solid #e5e7eb; background: #fff; display: flex; flex-direction: column; overflow: hidden; }
/* 树节点容器占满高度（不额外设置滚动，避免双滚动条互相影响） */
.ticket-query .tq-tree { min-height: 100%; }
/* 左侧折叠按钮：贴合左右列边界并在两种状态切换位置 */
.ticket-query .tq-left-toggle { position: absolute; top: 50%; left: var(--left-width, 230px); transform: translate(-50%, -50%); width: 18px; height: 36px; border: 1px solid #e6e6e6; background: #fff; border-radius: 0 8px 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: inline-flex; align-items: center; justify-content: center; z-index: 1000; cursor: pointer; pointer-events: auto; color: #0b57d0; }
.ticket-query .tq-left-toggle .chev { font-size: 18px; font-weight: 300; line-height: 1; color: inherit; }
.ticket-query .tq-left-toggle:hover { background: #fff; }
.ticket-query .collapsed-left .tq-left-toggle { left: 0; transform: translate(0, -50%); border-radius: 0 8px 8px 0; }
/* 右侧区域采用纵向布局，内部各块根据自身逻辑设置高度；右区不出现外层滚动条 */
.ticket-query .tq-right { min-width: 0; height: 100%; overflow: hidden; display: flex; flex-direction: column; padding-bottom: 16px; }
/* 查询结果主体允许内部滚动，由 ResultTable 控制子区域 */
.ticket-query .tq-result { flex: 1 1 auto; min-height: 140px; overflow: hidden; display: grid; grid-template-rows: 1fr auto; position: relative; padding-bottom: 0; }

/* 细化 DB 多选下拉，防止遮挡与滚动冲突（只针对 ticket.query 作用域） */
.ticket-query .tq-db-panel { max-height: min(60vh, 520px); overflow: auto; }
.ticket-query .tq-db-list { max-height: min(50vh, 420px); overflow: auto; }
button.warn { border-color: #ffb3b3; color: #a40000; background:#ffecec; }
button.warn:hover { background:#ffe0e0; }

/* ===== SQL 编辑区紧凑型标签栏 ===== */
.tq-tabbar { display: flex; align-items: center; gap: 6px; padding: 6px 6px 4px; border-bottom: 1px solid #e5e7eb; margin-bottom: 6px; }
.tq-tabbar .tq-tab { position: relative; display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; padding-right: 26px; background: #f3f4f6; border: 1px solid #e5e7eb; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; color: #0b57d0; font-size: 13px; font-weight: 400; overflow: visible; }
.tq-tabbar .tq-tab.active { background: #fff; border-color: #c7d2fe; z-index: 2; }
.tq-tabbar .tq-tab .ico { font-size: 12px; opacity: .8; }
.tq-tabbar .tq-tab .tit { max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tq-tabbar .tq-tab .dot { color: #9ca3af; margin-left: 2px; }
.tq-tabbar .tq-tab.active .dot { color: #ef4444; }
/* 关闭按钮变小并位于右上角 */
.tq-tabbar .tq-tab > .close { position: absolute; top: 2px; right: 3px; width: 14px; height: 14px; font-size: 11px; line-height: 12px; display: inline-flex; align-items: center; justify-content: center; border-radius: 3px; opacity: .8; cursor: pointer; padding: 0 !important; border: none !important; background: transparent !important; min-width: 0 !important; box-sizing: content-box; }
.tq-tabbar .tq-tab > .close:hover { background: #e5e7eb; opacity: 1; }
/* 新建（+）按钮：仅显示 +，无边框/背景，更紧凑 */
.tq-tabbar .tq-tab.add { border: none !important; background: transparent !important; padding: 0 6px !important; color: #0b57d0; font-size: 16px; line-height: 1; height: 24px; display: inline-flex; align-items: center; justify-content: center; }
.tq-tabbar .tq-tab.add:hover { background: transparent !important; color: #1d4ed8; }
button.info { border-color:#3b82f6; color:#0b57d0; background:#e8f0fe; }
button.info:hover { background:#dbe8ff; }
button.test { border-color:#22c55e; color:#15803d; background:#eefdf3; }
button.test:hover { background:#dcfce7; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { border: 1px solid #eee; padding: 8px; text-align: left; font-size: 14px; }
.table thead th { background: #f5f7ff; color: #0b57d0; font-weight: 400; }
.table td > button { font-size: 12px; padding: 4px 8px; border-radius: 4px; margin-right: 6px; }
.table td > button:last-child { margin-right: 0; }
.toolbar { margin-bottom: 8px; }
.toolbar select, .toolbar input { font-size: 14px; color: #0b57d0; font-weight: 400; }
.offscreen { position: absolute; left: -9999px; width: 0; height: 0; opacity: 0; pointer-events: none; }
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; border-radius:6px; border:1px solid #c9c9c9; background:#fff; color:#333; cursor:pointer; }
.icon-btn { width:36px; height:36px; }
.icon-btn.sm { width: 32px; height: 32px; }
.icon-btn.primary { border-color:#3b82f6; color:#0b57d0; }
.icon-btn.search { background:#eefdf3; border-color:#22c55e; color:#15803d; }
.icon-btn.search:hover { background:#dcfce7; }
.icon-btn.add { background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.icon-btn.add:hover { background:#dbe8ff; }
.icon-btn.warn { background:#fee2e2; border-color:#ef4444; color:#b91c1c; }
.icon-btn.warn:hover { background:#fecaca; }
.icon-btn:hover { background:#f5f7ff; }

/* 强制控制台工具栏按钮与下拉一致高度（32px），覆盖后续 .icon-btn 36px 规则 */
.ticket-query .tq-actions .icon-btn { width:32px !important; height:32px !important; border-radius:6px; }
.ticket-query .tq-actions .icon-btn svg { width:16px; height:16px; padding:0; }
.notice { margin-top: 12px; color: #555; }
/* 全局 toast（右上角，置顶显示） */
.mask-password { -webkit-text-security: disc; }
.global-notices { position: fixed; top: 16px; right: 16px; display: flex; flex-direction: column; gap: 8px; z-index: 3000; pointer-events: none; }
.global-notices .toast { background: #0b57d0; color: #fff; padding: 8px 12px; border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.18); font-size: 13px; max-width: 360px; pointer-events: auto; }
/* card & layout */
.card { background: #fff; border: 1px solid #e6e6e6; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.06); }
.section-block { padding: 12px 12px; margin: 16px 0; }
.pagination { display: flex; align-items: center; gap: 8px; padding: 10px 0 0; color: #0b57d0; font-weight: 400; font-size: 14px; }
.pagination select { color: #0b57d0; font-weight: 400; font-size: 14px; }
/* 工单查询布局 */
/* 让 ticket.query 外层容器在 preview 中自适应填满，可滚动的内容容器 */
.ticket-query.container { margin-bottom: 0; display: flex; flex-direction: column; flex: 1 1 auto; min-height: 0; padding-bottom: 0; padding-top: 0; }
/* 调整首卡片与 TAB 标题的顶部间距、以及两卡片之间的间距，使其与连接管理更贴近 */
.ticket-query .tq-toolbar.section-block { margin-top: 0px; margin-bottom: 6px; position: relative; overflow: visible; z-index: 2000; }
.ticket-query .tq-main.section-block { margin-top: 4px; margin-bottom: 0; }
/* TAB 标题已显示“工单查询”，隐藏页面内重复的大标题以消除多余上边距 */
.ticket-query > .section-title { display: none; }
/* 让卡片本身的底部与页面保持 5px（通过 tq-main 的 margin-bottom:5px 实现），因此这里去掉卡片底部 padding */
.ticket-query .tq-main.section-block { padding: 12px 12px 0; margin-bottom: 0 !important; }
/* 移除最后一个区块的底部外边距，避免额外空白 */
.ticket-query .section-block:last-of-type { margin-bottom: 0; }
/* 去除针对特定 data-v 的强制规则，统一由 JS 精准控制高度 */
.ticket-query .tq-toolbar .tq-toolbar-row { display:grid; grid-template-columns: var(--left-width, 230px) minmax(220px, auto) 1fr auto; column-gap: 14px; align-items:center; }
/* 四个区域（连接、数据库、过滤、按钮）均左对齐 */
.ticket-query .tq-toolbar .tq-toolbar-row > * { justify-self: start; }
/* 前三列容器占满各自列宽 */
.ticket-query .tq-toolbar .tq-toolbar-row > .icon-label { width: 100%; }
/* 连接列：使用 flex 承载图标与只读框，避免内容溢出到第二列 */
.ticket-query .tq-toolbar .tq-toolbar-row .tq-conn { display:flex; align-items:center; gap:6px; width:100%; min-width:0; overflow: hidden; position: relative; z-index: 1; }
/* 让工单查询顶部下拉与输入与全局工具条字体风格保持一致 */
.ticket-query .tq-toolbar select,
.ticket-query .tq-toolbar input { font-size: 14px; color: #0b57d0; font-weight: 400; height: 32px; line-height: 22px; padding: 4px 8px; box-sizing: border-box; border: 1px solid #c7d2fe; border-radius: 6px; background: #fff; }
.ticket-query .tq-toolbar .grow { flex:1; min-width: 160px; }
.ticket-query .tq-main { display:grid; grid-template-columns: 270px 1fr; gap:12px; min-height: 420px; position: relative; margin-bottom: 0; height: auto; max-height: none; overflow: hidden; align-items: stretch; align-content: stretch; flex: 1 1 auto; min-height: 0; }
.ticket-query .tq-left { border-right: 1px dashed #e5e7eb; padding-right: 8px; height: 100%; max-height: inherit; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.ticket-query .tq-right { display:flex; flex-direction: column; gap: 0px; min-width: 0; height: 100%; max-height: inherit; min-height: 0; overflow: hidden; padding-bottom: 16px; }
.ticket-query .tq-tree { flex: 1 1 auto; min-height: 0; overflow: auto; }
.ticket-query .tq-tree { max-height: 600px; }
.ticket-query .tq-tree-db-name { display:flex; align-items:center; gap:6px; padding: 6px 8px; border-radius: 6px; cursor: pointer; color: inherit; font-size: 14px; font-weight: 400; font-family: inherit; }
.ticket-query .tq-tree-db-name:hover { background:#f3f4f6; }
.ticket-query .tq-tree-db-list { list-style:none; margin: 4px 0 8px; padding:0; }
.ticket-query .tq-tree-db-list li { padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.ticket-query .tq-tree-db-list li:hover { background:#f3f4f6; }
.ticket-query .tq-tree-tables { list-style:none; margin: 2px 0 8px 28px; padding:0; }
/* 统一连接列字体风格，与其它列一致（去除任何特殊加粗/颜色/边框） */
.ticket-query :deep(.conn-col),
.ticket-query :deep(td.conn),
.ticket-query :deep(th.conn) {
  font-weight: 400;
  color: inherit;
  border: none;
  background: transparent;
  font-family: inherit;
}
.ticket-query .tq-db-multi { position: relative; min-width: 220px; max-width: 260px; font-size: 14px; line-height: 1.4; }
.ticket-query .tq-db-multi.disabled { opacity: .6; pointer-events: none; }
.ticket-query .tq-db-summary { display:flex; align-items:center; gap:6px; flex-wrap: nowrap; min-height: 32px; height: 32px; padding: 4px 8px; border:1px solid #c7d2fe; border-radius: 6px; background:#fff; cursor: pointer; white-space: nowrap; overflow: hidden; min-width: 240px; }
.ticket-query .tq-db-summary .tag { background:#f3f4f6; border-radius: 4px; padding: 2px 6px; font-size: 12px; max-width: 150px; overflow: hidden; text-overflow: ellipsis; }
.ticket-query .tq-db-summary .placeholder { color:#9ca3af; }
.ticket-query .tq-db-summary .caret { margin-left: auto; color:#64748b; }
.ticket-query .tq-db-multi { position: relative; display: inline-block; min-width: 240px !important; max-width: none !important; width: auto; }
.ticket-query .tq-db-panel { position: absolute; z-index: 20; margin-top: 6px; left: 0; right: 0; width: auto; max-height: 320px; overflow: visible; border: 1px solid #e5e7eb; border-radius: 8px; background:#fff; box-shadow: 0 8px 16px rgba(0,0,0,.08); padding: 8px; font-size: 14px; line-height: 1.4; box-sizing: border-box; }
.ticket-query .tq-db-search-wrap { position: relative; z-index: 0; }
.ticket-query .tq-db-search { position: relative; z-index: 0; width: 100%; padding: 6px 40px 6px 8px; border: 1px solid #e5e7eb; border-radius: 6px; font-size: 13px; background: #fff; box-sizing: border-box; }
.ticket-query .tq-db-search-wrap + .tq-db-list { margin-top: 8px; }
.ticket-query .tq-db-clear { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); width: 24px; height: 24px; display: inline-flex !important; align-items: center; justify-content: center; border: none; background: transparent; color: #111827; cursor: pointer; z-index: 999 !important; border-radius: 4px; font-size: 18px; line-height: 1; }
.ticket-query .tq-db-clear:hover { color: #374151; background: #f3f4f6; }
.ticket-query .tq-db-clear svg { width: 18px; height: 18px; }
.ticket-query .tq-db-list { margin-top: 8px; display: flex; flex-direction: column; gap: 2px; max-height: 260px; overflow: auto; }
.ticket-query .tq-db-panel .tq-db-list label.opt { position: relative; display: block !important; font-size: 13px; padding: 6px 32px 6px 8px; width: max-content; min-width: 100%; box-sizing: border-box; text-align: left; white-space: nowrap; color: #111827; }
.ticket-query .tq-db-panel .tq-db-list label.opt .txt { margin: 0 !important; min-width: 0; overflow: visible; text-overflow: clip; white-space: nowrap; text-align: left; display: inline-block; color: #111827; font-size: 13px; line-height: 20px; }
.ticket-query .tq-db-panel .tq-db-list label.opt input[type="checkbox"] { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; margin: 0; display: inline-block; appearance: auto; -webkit-appearance: checkbox; }
.ticket-query .tq-db-panel .tq-db-list label.opt:hover { background: #f9fafb; border-radius: 4px; }
.ticket-query .tq-db-footer { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
.ticket-query .tq-db-footer .btn.sm { padding: 4px 10px; font-size: 12px; border: 1px solid #e5e7eb; border-radius: 4px; background:#fff; cursor: pointer; }
.ticket-query .tq-db-footer .btn.sm.ghost { background: transparent; }
.ticket-query .muted { color:#6b7280; font-size: 13px; padding: 4px 6px; }
.ticket-query .arrow { transition: transform .18s ease; display:inline-block; transform: rotate(90deg); }
.ticket-query .arrow.open { transform: rotate(270deg); }
.ticket-query .tq-editor { display:flex; flex-direction: column; flex: 0 0 var(--tq-editor-h, auto); min-height: 100px; position: relative; z-index: 20; overflow: visible; }
/* CodeMirror 容器：自身不加内边距和边框，避免阻挡编辑器点击区域；尺寸由内部 .cm-editor 承担 */
.ticket-query .tq-sql { width: 100%; height: 100%; min-height: 0; flex: 1 1 auto; resize: none; padding: 0; border: none; border-radius: 0; position: relative; overflow: hidden; }
/* 让 CodeMirror 编辑器占满容器并具备原有输入样式 */
.ticket-query .tq-sql :deep(.cm-editor) {
  width: 100%;
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  padding: 10px;
  border:1px solid #e5e7eb;
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 13px;
  line-height: 1.6;
}
/* 编辑区域行内换行，避免超长行撑破布局 */
.ticket-query .tq-sql :deep(.cm-editor .cm-content) { white-space: pre-wrap; }
.tq-resizer, .ticket-query .tq-resizer { display: none !important; }
.tq-resizer::before, .tq-resizer::after { display: none !important; content: none !important; }
.ticket-query .tq-sql :deep(.cm-tooltip) { z-index: 3000; }
.ticket-query .tq-sql :deep(.cm-tooltip-autocomplete) { z-index: 3001; }
.ticket-query .tq-result .tq-result-body { display: flex; flex-direction: column; width: 100%; flex: 1 1 auto; min-height: 0; overflow: auto; grid-row: 1; }
.ticket-query .tq-result .tq-table-fixed { display: flex; flex-direction: column; width: 100%; flex: 1 1 0%; min-height: 0; }
.ticket-query .tq-result .tq-body { width: 100%; max-width: 100%; flex: 1 1 0%; min-height: 0; max-height: 100%; overflow-x: auto; overflow-y: auto; -webkit-overflow-scrolling: touch; padding-bottom: 0; box-sizing: border-box; }
.ticket-query .tq-result .tq-pagination { display: flex; align-items: center; gap: 8px; width: 100%; height: 44px; padding: 10px 12px; text-align: left; flex: 0 0 auto; position: static; background: #fff; border-top: 1px solid #e5e7eb; margin-top: 0; box-sizing: border-box; z-index: 1; grid-row: 2; }
.ticket-query .tq-vsplit { height: 6px; flex: 0 0 6px; display: block; background: transparent; cursor: row-resize; margin: -1px 0 0 0; position: relative; z-index: 20; border: 0; box-shadow: none; border-top: 0; }
/* 只保留细线把手，移除粗把手 */
.ticket-query .tq-vsplit::after { display: none !important; content: none !important; }
.ticket-query .tq-vsplit::before { content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 2px; background: #cbd5e1; border-radius: 2px; }
.modal .tq-vsplit::before { box-shadow: none; }
/* 浮动窗口：隐藏编辑器底边线，避免分隔条上方出现细线 */
/* 浮动窗口：由外层容器绘制唯一一圈更浅的常驻边框 */
.modal .tq-editor { border: 1px solid #edf2f7 !important; border-radius: 8px; }
/* 移除内部 .cm-editor 及其子元素所有边框，避免出现第二圈边框 */
.modal .tq-editor :deep(.cm-editor) { border: none !important; }
.modal .tq-editor :deep(.cm-editor:hover),
.modal .tq-editor :deep(.cm-editor.cm-focused),
.modal .tq-editor :deep(.cm-editor:focus),
.modal .tq-editor :deep(.cm-editor:focus-visible),
.modal .tq-editor :deep(.cm-editor:focus-within) {
  outline: none !important;
  box-shadow: none !important;
  border-color: transparent !important;
}
/* 包装容器不再需要单独的下边隐藏 */
/* 避免内部滚动/内容再叠加第二圈边框 */
.modal .tq-editor :deep(.cm-scroller),
.modal .tq-editor :deep(.cm-content) {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}
/* 容器不增加悬停边框，边框只由 .cm-editor 控制 */
.modal .tq-editor-wrap { border: none !important; }
/* 彻底去掉编辑器获得焦点时的额外描边（可能来自默认主题） */
.modal .tq-editor :deep(.cm-editor *:focus),
.modal .tq-editor :deep(.cm-editor *:focus-visible),
.modal .tq-editor :deep(.cm-editor *:focus-within) {
  outline: none !important;
  box-shadow: none !important;
}
.ticket-query .tq-vsplit:hover::before { background: #94a3b8; }
.ticket-query .tq-head-inner { display: inline-block; min-height: 36px; height: 36px; flex: 0 0 auto; }
.ticket-query .tq-head-inner table { height: 36px; }
/* thead+body 同步宽度，thead 粘顶 */
.ticket-query .tq-table { border-collapse: separate; border-spacing: 0; width: max-content; table-layout: fixed; }
.ticket-query .tq-table thead { position: sticky; top: 0; z-index: 2; background: #f5f7ff; }
.ticket-query .tq-table thead th { background: #f5f7ff; position: relative; }
/* 冻结的正文单元格 */
.ticket-query .tq-table tbody .freeze-cell { position: sticky; background: #fff; z-index: 4; top: auto; }
/* 仅冻结列的表头内部容器参与横向 sticky；普通列不 sticky，避免跟随滚动产生“漂移” */
.ticket-query .tq-table thead .th-inner { position: relative; background: transparent; z-index: auto; }
/* 冻结表头单元格：自身 sticky，配合内联 left 偏移 */
.ticket-query .tq-table thead th.freeze-head { position: sticky; left: 0; background: #f5f7ff; z-index: 12; }
/* 冻结列右侧描边（头/体统一视觉） */
.ticket-query .tq-table thead th.freeze-head::after,
.ticket-query .tq-table .freeze-cell::after { content: ''; position: absolute; top: 0; right: -1px; width: 1px; height: 100%; background: #e5e7eb; }
.ticket-query .tq-table .th-inner { display: flex; align-items: center; gap: 6px; padding-right: 0; }
.ticket-query .tq-table .th-title { flex: 1 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
.ticket-query .tq-table .th-actions { position: static; transform: none; right: auto; top: auto; display: inline-flex; gap: 6px; flex: 0 0 auto; margin-right: 6px; z-index: 2; }
.ticket-query .tq-table .th-btn { width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; border: none; background: transparent; color: #64748b; cursor: pointer; padding: 0; }
.ticket-query .tq-table .th-btn:hover { color: #0b57d0; }
.ticket-query .tq-table .th-btn svg { width: 16px; height: 16px; }
.ticket-query .tq-table .col-resizer { position: absolute; top: 0; right: 0; width: 4px; height: 100%; cursor: col-resize; user-select: none; z-index: 4; }
.ticket-query .tq-table .col-resizer:hover { background: rgba(59,130,246,0.15); }
.ticket-query .tq-table-tools { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; gap: 8px; }
.ticket-query .tq-table-tools .tq-input { width: 80px; padding: 4px 6px; border: 1px solid #e5e7eb; border-radius: 4px; }
.ticket-query .tq-table-tools .btn { padding: 4px 10px; border: 1px solid #e5e7eb; background: #fff; border-radius: 4px; cursor: pointer; }
.ticket-query .tq-table-tools .btn:hover { background: #f3f4f6; }
.ticket-query .tq-body { scrollbar-width: auto; }
.ticket-query .tq-scroll-x { scrollbar-width: auto; }
.ticket-query .tq-body { scrollbar-width: thin; scrollbar-color: #94a3b8 transparent; }
.ticket-query .tq-body::-webkit-scrollbar { width: 10px; height: 10px; }
.ticket-query .tq-body::-webkit-scrollbar:horizontal { height: 0 !important; background: transparent !important; }
/* 表头隐藏滚动条（避免顶部出现横向滚动条） */
.ticket-query .tq-scroll-x { scrollbar-width: none; }
.ticket-query .tq-scroll-x::-webkit-scrollbar { width: 0 !important; height: 0 !important; background: transparent !important; }
.ticket-query .tq-scroll-x::-webkit-scrollbar-thumb { background: transparent !important; }
.ticket-query .tq-body::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.ticket-query .tq-body::-webkit-scrollbar-thumb:hover { background: #64748b; }
.ticket-query .tq-body::-webkit-scrollbar-thumb:active { background: #64748b; }
.ticket-query .tq-body::-webkit-scrollbar-track { background: transparent; }
.ticket-query .tq-text { margin: 0; white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 13px; }
.ticket-query .tq-notices { position: absolute; right: 16px; top: 8px; display:flex; flex-direction: column; gap:6px; }
.ticket-query .tq-notice { background: #0b57d0; color: #fff; padding: 6px 10px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); font-size: 13px; max-width: 360px; }
/* 左侧连接树显隐开关，风格贴近主菜单按钮 */
/* unified position & style defined above */
.ticket-query .collapsed-left .tq-left { padding-right: 0; border-right: none; overflow: hidden; }
/* toolbar icons uniform */
.ticket-query .icon-label { display:inline-flex; flex-direction: row; align-items:center; gap:2px; white-space: nowrap; }
/* 缩小图标占位，贴近右侧输入/下拉 */
.ticket-query .icon-label .mi { width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center; border-radius:0; color:#0b57d0; background:transparent; border:none; }
.ticket-query .icon-label .mi svg { width:16px; height:16px; }
.ticket-query .icon-label select,
.ticket-query .icon-label input { height:32px; padding: 4px 8px; box-sizing: border-box; }
.ticket-query .tq-toolbar-row select,
.ticket-query .tq-toolbar-row input { border-color:#c7d2fe; }
.ticket-query .tq-toolbar-row .tq-conn { width: auto; max-width: 100%; margin-right: 0; }
/* 数据库列与过滤列的左右间距 */
.ticket-query .tq-toolbar .tq-toolbar-row label[aria-label="数据库"] { margin-right: 0; min-width: 220px; }
.ticket-query .tq-toolbar .tq-toolbar-row .tq-filter { margin-right: 0; }
.ticket-query .tq-toolbar-row .tq-conn select { width: 100%; min-width: 0; }
/* 只读连接展示也限制为 230px，和左侧树保持对齐 */
.ticket-query .tq-toolbar-row .tq-conn .tq-conn-readonly {
  flex: 1 1 auto;
  min-width: 0;
  height: 32px;
  line-height: 22px;
  padding: 4px 8px;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  background: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  box-sizing: border-box;
}
/* 第二列：数据库下拉左对齐，允许在等分列内自适应 */
.ticket-query .tq-toolbar-row label[aria-label="数据库"] { justify-self: start; min-width: 0; width: 100%; }
/* 数据库下拉容器允许收缩，不与相邻控件重叠 */
.ticket-query .tq-db-multi { min-width: 0; position: relative; z-index: 0; }
/* 数据库下拉总结条占满第二列，文本溢出省略 */
.ticket-query .tq-db-summary { width: 100%; box-sizing: border-box; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
/* 第三列过滤框占满列宽 */
.ticket-query .tq-filter input { width: 100%; }
/* 第四列按钮组左对齐 */
.ticket-query .tq-actions { justify-self: start; display: inline-flex; gap: 8px; margin-left: -6px; }
/* 工具栏按钮尺寸与下拉/输入保持一致（32px） */
.ticket-query .tq-actions .icon-btn { width: 32px; height: 32px; border-radius: 6px; }
.ticket-query .tq-actions .icon-btn svg { width: 16px; height: 16px; padding: 0; }

/* 暂时还原拖动条与结果区为原有风格，避免影响工单查询调试 */
.ticket-query .tq-editor-wrap { border: none; }
.ticket-query .tq-editor-wrap .cm-editor { height: 100%; }
.ticket-query .tq-vsplit { height: 4px; background: transparent; cursor: default; margin: 4px 0; }
/* 结果体滚动，分页固定在下方可见 */
.ticket-query .tq-result-body { flex: 1 1 auto; overflow: auto; }
.ticket-query .tq-pagination { display: flex; align-items: center; gap: 8px; padding-top: 8px; border-top: 1px dashed #e5e7eb; }
/* 数据库多选下拉：外部点击关闭的全屏透明遮罩 + 层级 */
.ticket-query .tq-db-multi { position: relative; }
.ticket-query .tq-db-overlay { position: fixed; left: 0; top: 0; right: 0; bottom: 0; z-index: 3001; background: transparent; }
.ticket-query .tq-db-panel { position: absolute; z-index: 3002; }
/* 数据库菜单区字体与连接列表保持一致；表名字号小一号 */
.ticket-query .tq-left .tq-tree { font-family: inherit; color: #0b57d0; }
.ticket-query .tq-left .tq-tree .tq-tree-db-name { font-size: 14px; font-weight: 400; color: #0b57d0; }
.ticket-query .tq-left .tq-tree .tq-tree-db-name .arrow { color: #0b57d0; }
.ticket-query .tq-left .tq-tree .tq-tree-tables li { font-size: 13px; color: #374151; line-height: 1.6; }
.ticket-query .tq-left .tq-tree .tq-tree-tables li.muted { color: #6b7280; }
.ticket-query .tq-left .tq-tree .tq-tree-tables li:hover { background: #f5f7ff; color: #0b57d0; }
/* 左侧库名区域的过滤按钮交互 */
.ticket-query .tq-left .tq-tree .tq-tree-db { position: relative; }
.ticket-query .tq-left .tq-tree .tq-tree-db-name { display:flex; align-items:center; justify-content:flex-start; gap:6px; }
.ticket-query .tq-left .tq-tree .tq-db-filter-btn { margin-left:auto; opacity:0; pointer-events:none; background:transparent; border:none; color:#6b7280; cursor:pointer; padding:2px; border-radius:4px; transition:opacity .15s, color .15s, background .15s; }
.ticket-query .tq-left .tq-tree .tq-tree-db:hover .tq-db-filter-btn { opacity:1; pointer-events:auto; }
.ticket-query .tq-left .tq-tree .tq-db-filter-btn:hover { background:#eef2ff; color:#0b57d0; }
.ticket-query .tq-left .tq-tree .tq-db-filter-btn.active { opacity:1; pointer-events:auto; color:#0b57d0; }
/* 浮动过滤框样式 */
.ticket-query .tq-left .tq-tree .tq-table-filter-pop { position:absolute; top:28px; right:8px; z-index: 10; background:#fff; border:1px solid #c7d2fe; border-radius:6px; padding:6px; box-shadow: 0 6px 14px rgba(99,102,241,.18); display:flex; align-items:center; gap:6px; }
.ticket-query .tq-left .tq-tree .tq-table-filter-pop .tq-table-filter { width:180px; padding:6px 8px; border:1px solid #c7d2fe; border-radius:4px; outline:none; }
.ticket-query .tq-left .tq-tree .tq-table-filter-pop .tq-table-filter:focus { box-shadow: 0 0 0 2px rgba(99,102,241,.25); }
.ticket-query .tq-left .tq-tree .tq-table-filter-pop .tq-table-filter-clear { background:transparent; border:none; color:#6b7280; cursor:pointer; font-size:16px; line-height:1; }
/* filter width constraint */
.ticket-query .tq-filter input { width: 280px; max-width: 40vw; }
/* modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { width: 720px; max-width: 92vw; background: #fff; border-radius: 12px; box-shadow: 0 8px 28px rgba(0,0,0,0.24); overflow: hidden; font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; }
.modal-header { background: linear-gradient(90deg, #e8f0fe 0%, #dbe8ff 100%); color: #0b57d0; padding: 14px 18px; border-bottom: 1px solid #c7d2fe; }
.modal-header h2 { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: .2px; }
.modal-header h2.with-icon { display: inline-flex; align-items: center; gap: 8px; }

/* 调整命令按钮内图标的额外间距（+2px）且保证 Firefox 不遮挡关闭图标 */
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border:1px solid #d0d7de; border-radius:8px; background:#fff; color:#0b57d0; position: relative; overflow: visible; }
.icon-btn svg { width: 22px; height: 22px; padding: 2px; box-sizing: content-box; }
/* 各种状态维持原有配色 */
.icon-btn.primary { border-color:#3b82f6; color:#0b57d0; }
.icon-btn.search { background:#eefdf3; border-color:#22c55e; color:#15803d; }
.icon-btn.search:hover { background:#dcfce7; }
.icon-btn.add { background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.icon-btn.add:hover { background:#dbe8ff; }
.icon-btn.warn { background:#fee2e2; border-color:#ef4444; color:#b91c1c; }
.icon-btn.warn:hover { background:#fecaca; }
.icon-btn:hover { background:#f5f7ff; }

/* Firefox 标签页：避免伪元素或背景覆盖关闭按钮，明确层级 */
.tabs-bar { position: relative; z-index: 1; }
.tab-item { position: relative; z-index: 1; background-clip: padding-box; }
.tab-item .close, .tab-item :deep(.close) { position: relative; z-index: 3; pointer-events: auto; }
.modal-header h2.with-icon svg { width: 18px; height: 18px; }
.modal-body { padding: 16px; }
.modal-header.warn { background: linear-gradient(90deg, #fee2e2 0%, #ffedd5 100%); color: #b91c1c; border-bottom: 1px solid #fecaca; }
.confirm-modal { width: 520px; max-width: 92vw; }
.confirm-content .confirm-text { margin: 0; line-height: 1.6; }
.confirm-content .confirm-subtext { margin: 6px 0 0; color: #6b7280; font-size: 13px; }
.modal-actions { padding: 0 16px 16px; display: flex; justify-content: center; gap: 10px; }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } .grid .span-2 { grid-column: span 1; } }
.ticket-query .tq-left-tools { position: sticky; top: 0; z-index: 2; background: #fff; display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-bottom: 1px solid #e5e7eb; }
.ticket-query .tq-left .tq-db-toggle { height: 28px; padding: 0 10px; border: 1px solid #c7d2fe; border-radius: 6px; background: #fff; color: #0b57d0; cursor: pointer; }
.ticket-query .tq-left .tq-db-toggle.show { background: #e8f0fe; border-color: #3b82f6; }
.ticket-query .tq-left .tq-db-toggle:hover { background: #f5f7ff; }
.ticket-query .tq-left .tq-db-toggle:active { background: #e5e7eb; }

@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } .grid .span-2 { grid-column: span 1; } }
.ticket-query .tq-left-tools { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-bottom: 1px solid #e5e7eb; }
.ticket-query .tq-left .tq-db-toggle { height: 28px; padding: 0 10px; border: 1px solid #c7d2fe; border-radius: 6px; background: #fff; color: #0b57d0; cursor: pointer; }
.ticket-query .tq-left .tq-db-toggle.show { background: #e8f0fe; border-color: #3b82f6; }
.ticket-query .tq-left .tq-db-toggle:hover { background: #f5f7ff; }
.ticket-query .tq-left .tq-db-toggle:active { background: #e5e7eb; }
</style>

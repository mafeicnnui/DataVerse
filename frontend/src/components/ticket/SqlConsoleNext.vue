<template>
  <div class="sql-next">
    <header class="hdr">
      <img class="brand" src="/dataverse_logo.png" alt="logo" />
      <div class="title">星域SQL控制台</div>
      <div class="big-actions" style="margin-left:auto">
        <button class="big-btn" title="新建查询" @click="newTab()">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 13H13v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
          <span>新建查询</span>
        </button>
        <button class="big-btn" title="表" @click="openObjectTab('tables')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 5h16v4H4V5zm0 5h16v4H4v-4zm0 5h16v4H4v-4z"/></svg>
          <span>表</span>
        </button>
        <button class="big-btn" title="视图" @click="openObjectTab('views')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 5C5 5 2 12 2 12s3 7 10 7 10-7 10-7-3-7-10-7zm0 2a5 5 0 110 10 5 5 0 010-10z"/></svg>
          <span>视图</span>
        </button>
        <button class="big-btn" title="函数" @click="openObjectTab('functions')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4h10v2H9v5h4a4 4 0 110 8H7v-2h6a2 2 0 100-4H7V4z"/></svg>
          <span>函数</span>
        </button>
        <button class="big-btn" title="过程" @click="openObjectTab('procedures')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h16v4H4V4zm0 6h10v4H4v-4zm0 6h16v4H4v-4z"/></svg>
          <span>过程</span>
        </button>
        <button class="big-btn" title="事件" @click="openObjectTab('events')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v2H5a2 2 0 00-2 2v12a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2h-2V2h-2v2H9V2H7zm12 6H5v10h14V8z"/></svg>
          <span>事件</span>
        </button>
        <button class="big-btn" title="触发器" @click="openObjectTab('triggers')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2 4 20l8-4 8 4-8-18z"/></svg>
          <span>触发器</span>
        </button>
      </div>
    </header>
    <div class="layout" :style="{ '--left-w': leftWidth + 'px' }">
    <!-- 左侧：三层树（实例->库->表） + 全局搜索 -->
    <aside class="left">
        <div class="tree" role="tree">
          <div class="inst" v-for="inst in instances" :key="'i-'+inst.id">
            <div class="inst-hd" @click="toggleConn(inst.id)" @mouseenter="hoverInst=inst.id" @mouseleave="hoverInst=''">
              <span class="arrow" :class="{open: expandConn[inst.id]}" aria-hidden="true">›</span>
              <svg class="ico inst" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 4h18v8H3V4zm2 2v4h14V6H5zm-2 8h18v6H3v-6zm2 2v2h6v-2H5zm8 0v2h6v-2h-6z"/></svg>
              <span class="label" :title="inst.ip + ':' + inst.port">
                {{ inst.description || (inst.ip + ':' + inst.port) || ('#' + inst.id) }}
              </span>
              <button v-show="hoverInst===inst.id || hasInstFilter(inst.id)" class="mini filter" :class="{ active: hasInstFilter(inst.id) }" title="选择实例库" @click.stop="openInstFilter(inst, $event)">⚙</button>
            </div>
            <!-- 实例库过滤面板（按钮同水平位置显示，包含搜索框；鼠标移出自动关闭） -->
            <div
              v-if="instFilterVisible===inst.id"
              class="panel inst-panel"
              :style="{ left: instPanelPos.left + 'px', top: instPanelPos.top + 'px' }"
              @mousedown.stop
              @mouseleave="instFilterVisible=''"
            >
              <div class="ph-search">
                <span class="ico" aria-hidden="true">🔍</span>
                <input v-model.trim="instSearch" placeholder="搜索数据库..." />
                <button class="clear" :title="'清空所选库'" @click="clearInstSelected(inst.id)">🧹</button>
              </div>
              <div class="plist">
                <label class="opt" v-for="db in (filterInstDbs(inst.id))" :key="'p-'+inst.id+'-'+db">
                  <input type="checkbox" :checked="isDbSelected(inst.id, db)" @change="onDbSelect(inst.id, db, $event)">
                  <span>{{ db }}</span>
                </label>
              </div>
            </div>
            <ul v-show="expandConn[inst.id]" class="dbs">
              <li class="db" v-for="db in filteredDbList(inst.id)" :key="'db-'+inst.id+'-'+db">
                <div class="db-hd" @click="toggleDb(inst.id, db)" @mouseenter="hoverDb=inst.id+':'+db" @mouseleave="onDbMouseLeave(inst.id, db)">
                  <span class="arrow" :class="{open: !!expandDbByConn[inst.id]?.[db]}" aria-hidden="true">›</span>
                  <svg class="ico db" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3c-4.97 0-9 1.79-9 4v10c0 2.21 4.03 4 9 4s9-1.79 9-4V7c0-2.21-4.03-4-9-4zm0 2c3.87 0 7 .9 7 2s-3.13 2-7 2-7-.9-7-2 3.13-2 7-2zm0 6c3.87 0 7-.9 7-2v3c0 1.1-3.13 2-7 2s-7-.9-7-2V9c0 1.1 3.13 2 7 2zm0 7c-3.87 0-7-.9-7-2v-3c0 1.1 3.13 2 7 2s7-.9 7-2v3c0 1.1-3.13 2-7 2z"/></svg>
                  <span class="label" :title="db">{{ db }}</span>
                  <button
                    v-show="hoverDb===inst.id+':'+db || !!dbFilterTextByKey[keyOf(inst.id, db)] || dbFilterVisibleKey===keyOf(inst.id, db)"
                    class="mini filter"
                    :class="{ active: !!dbFilterTextByKey[keyOf(inst.id, db)] }"
                    :title="dbFilterTextByKey[keyOf(inst.id, db)] ? '已过滤：' + dbFilterTextByKey[keyOf(inst.id, db)] : '过滤该库的表'"
                    @click.stop="showDbFilterPopup(inst.id, db, $event)"
                  >🔍</button>
                  <input v-if="dbFilterVisibleKey==='__inline__never__'" class="db-filter-input" />
                </div>
                <!-- 数据库展开后的分类菜单 -->
                <ul v-show="expandDbByConn[inst.id]?.[db]" class="cats">
                  <!-- Tables 分类 -->
                  <li class="cat">
                    <div class="cat-hd" @click="toggleDbCategory(inst.id, db, 'tables')">
                      <span class="arrow" :class="{open: isDbCatOpen(inst.id, db, 'tables')}" aria-hidden="true">›</span>
                      <svg class="ico cat-tables" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 5h16v4H4V5zm0 5h16v4H4v-4zm0 5h16v4H4v-4z"/></svg>
                      <span class="label">Tables</span>
                    </div>
                    <ul class="tbls" v-show="isDbCatOpen(inst.id, db, 'tables')">
                      <li class="tbl" v-for="t in filteredTablesForDisplay(inst.id, db)" :key="'t-'+inst.id+'-'+db+'-'+t">
                        <div class="table-hd">
                          <span class="arrow" :class="{open: isTableOpen(inst.id, db, t)}" @click.stop="toggleTableCats(inst.id, db, t)" aria-hidden="true">›</span>
                          <svg class="ico tbl" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 5h18v14H3V5zm2 2v2h14V7H5zm0 4v2h14v-2H5zm0 4v2h14v-2H5z"/></svg>
                          <span class="label" @click.stop="toggleTableCats(inst.id, db, t)">{{ t }}</span>
                          <div class="inline-actions" aria-label="表操作">
                            <button class="tb-act" title="新建查询" @click.stop="insertQuickQuery(db, t)">
                              <!-- 加号：表示为该表新建查询 -->
                              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                            </button>
                            <button class="tb-act" title="查看对象信息" @click.stop="openInspector(inst.id, db, t)">
                              <!-- 眼睛：查看对象信息（DDL/元数据） -->
                              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7zm0 2a5 5 0 110 10 5 5 0 010-10z"/></svg>
                            </button>
                          </div>
                        </div>
                        <!-- 每个表的子分类（列/索引/外键/触发器/事件） -->
                        <ul class="table-cats" v-show="isTableOpen(inst.id, db, t)">
                          <li class="subcat" @click.stop="(ensurePrimaryColumns(inst.id, db, t), toggleTableColumns(inst.id, db, t))">
                            <svg class="ico col" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h10v2H4v-2z"/></svg>
                            <span>Columns</span>
                          </li>
                          <ul v-show="isColumnsOpen(inst.id, db, t)" class="columns">
                            <li class="muted" v-if="isColsLoading(inst.id, db, t)">加载中...</li>
                            <li class="col-name" v-for="c in getColumns(inst.id, db, t)" :key="'c-'+inst.id+'-'+db+'-'+t+'-'+c">
                              <svg v-if="isPrimaryKey(inst.id, db, t, c)" class="ico pk" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 14a5 5 0 1 1 3.9 4.9L9 22H7v-2H5v-2H3v-2h4.1A5 5 0 0 1 7 14Zm8-5a3 3 0 1 0-6 0a3 3 0 0 0 6 0Z"/></svg>
                              <svg v-else class="ico col2" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h10v2H4v-2z"/></svg>
                              <span class="name">{{ c }}</span>
                            </li>
                            <li class="muted" v-if="!isColsLoading(inst.id, db, t) && getColumns(inst.id, db, t).length===0">无列</li>
                          </ul>
                          <li class="subcat" @click.stop="toggleTableIndexes(inst.id, db, t)">
                            <svg class="ico idx" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z"/></svg>
                            <span>Indexes</span>
                          </li>
                          <ul v-show="isIndexesOpen(inst.id, db, t)" class="columns">
                            <li class="muted" v-if="isIdxLoading(inst.id, db, t)">加载中...</li>
                            <li class="col-name" v-for="ix in getNonPrimaryIndexes(inst.id, db, t)" :key="'i-'+inst.id+'-'+db+'-'+t+'-'+ix">
                              <svg class="ico idx2" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z"/></svg>
                              <span class="name">{{ ix }}</span>
                            </li>
                            <li class="muted" v-if="!isIdxLoading(inst.id, db, t) && getNonPrimaryIndexes(inst.id, db, t).length===0">无索引</li>
                          </ul>
                          <li class="subcat">
                            <svg class="ico fk" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 7h10v2H9v6H7V7zm10 6h-4v4h-2v-6h6v2z"/></svg>
                            <span>Foreign Keys</span>
                          </li>
                          <li class="subcat">
                            <svg class="ico trg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2 4 20l8-4 8 4-8-18z"/></svg>
                            <span>Triggers</span>
                          </li>
                          <li class="subcat">
                            <svg class="ico evt" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 2v2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2H7zm12 6H5v10h14V8z"/></svg>
                            <span>Events</span>
                          </li>
                        </ul>
                      </li>
                      <li class="muted" v-if="loadingKey(inst.id, db)">加载中...</li>
                      <li class="muted" v-else-if="emptyKey(inst.id, db)">无表</li>
                    </ul>
                  </li>
                  <!-- Views/Functions/Procedures/Events 分类（占位，可后续填充列表） -->
                  <li class="cat">
                    <div class="cat-hd" @click="toggleDbCategory(inst.id, db, 'views')">
                      <span class="arrow" :class="{open: isDbCatOpen(inst.id, db, 'views')}" aria-hidden="true">›</span>
                      <svg class="ico cat-views" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7zm0 2a5 5 0 110 10 5 5 0 010-10z"/></svg>
                      <span class="label">Views</span>
                    </div>
                  </li>
                  <li class="cat">
                    <div class="cat-hd" @click="toggleDbCategory(inst.id, db, 'functions')">
                      <span class="arrow" :class="{open: isDbCatOpen(inst.id, db, 'functions')}" aria-hidden="true">›</span>
                      <svg class="ico cat-func" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 4h10v2H9v5h4a4 4 0 110 8H7v-2h6a2 2 0 100-4H7V4z"/></svg>
                      <span class="label">Functions</span>
                    </div>
                  </li>
                  <li class="cat">
                    <div class="cat-hd" @click="toggleDbCategory(inst.id, db, 'procedures')">
                      <span class="arrow" :class="{open: isDbCatOpen(inst.id, db, 'procedures')}" aria-hidden="true">›</span>
                      <svg class="ico cat-proc" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h16v4H4V4zm0 6h10v4H4v-4zm0 6h16v4H4v-4z"/></svg>
                      <span class="label">Procedures</span>
                    </div>
                  </li>
                  <li class="cat">
                    <div class="cat-hd" @click="toggleDbCategory(inst.id, db, 'events')">
                      <span class="arrow" :class="{open: isDbCatOpen(inst.id, db, 'events')}" aria-hidden="true">›</span>
                      <svg class="ico cat-evt" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 2v2H5a2 2 0 00-2 2v12a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2h-2V2h-2v2H9V2H7zm12 6H5v10h14V8z"/></svg>
                      <span class="label">Events</span>
                    </div>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <div class="gsearch">
          <div class="searchbox">
            <span class="ico" aria-hidden="true">🔍</span>
            <input v-model.trim="globalDbSearch" placeholder="搜索" />
            <button class="mini action" title="清除所有过滤" @click="clearAllDbFilters">🧹</button>
            <button class="mini action" title="折叠菜单" @click="collapseAllDbs">📂</button>
          </div>
        </div>
      </aside>
      <div class="vsplit" @mousedown="startDrag"></div>
      <!-- 右侧：编辑器在上，结果在下（保持与旧页一致的按钮组） -->
      <main class="right" :class="{ 'inspector-on': inspectorVisible }" :style="{ '--left-w': leftWidth + 'px', '--insp-w': inspectorWidth + 'px' }" @mousemove="onDragHover">
        <!-- 浮动库表过滤输入框：允许跨出左侧区域显示在右侧 -->
        <input
          v-if="dbFilterPopup.show"
          class="db-filter-float"
          :style="{ left: dbFilterPopup.left + 'px', top: dbFilterPopup.top + 'px' }"
          :value="popupInputValue"
          @input="onPopupInput"
          @change="onPopupChange"
          @keydown.enter.prevent="onPopupConfirm"
          @mouseenter="popupHover = true"
          @mouseleave="popupHover = false; if(!dbFilterTextByKey[dbFilterPopup.key]) dbFilterPopup.show=false"
          placeholder="搜索"
        />
        <div class="tabs" style="grid-column:1; grid-row:1; z-index:2;">
          <SqlTabs :ctx="tq" />
          <ConfirmDialog
            :visible="confirmCloseVisible"
            :text="'确定要关闭当前 SQL 标签吗？未保存的内容将丢失。'"
            :meta="{ type: 'SQL 标签', env: connInfo }"
            @confirm="performCloseTab"
            @cancel="cancelCloseTab"
          />
        </div>
        <!-- 每个标签的连接/数据库工具条（置于 Tabs 下、与对象面板同级） -->
        <div class="tab-toolbar" style="grid-column:1; grid-row:2; z-index:2;">
          <select class="sel" v-model="activeConnId" :disabled="running" title="实例">
            <option v-for="inst in instances" :key="'sel-inst-'+inst.id" :value="inst.id">
              {{ inst.description || (inst.ip + ':' + inst.port) || ('#' + inst.id) }}
            </option>
          </select>
          <select class="sel" v-model="activeDatabase" :disabled="running" title="数据库">
            <option value="">选择数据库</option>
            <option v-for="db in (dbsByConn[activeConnId]||[])" :key="'sel-db-'+activeConnId+'-'+db" :value="db">{{ db }}</option>
          </select>
          <button class="icon-btn add" :disabled="running" @click="exec" title="执行"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>
          <button class="icon-btn warn" :disabled="!running" @click="stop" title="停止"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg></button>
          <button class="icon-btn" :disabled="running" @click="viewPlan" title="执行计划"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg></button>
          <button class="icon-btn info" :disabled="running" @click="beautify" title="格式化"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/></svg></button>
          <button class="icon-btn" :disabled="running" @click="exportCSV" title="导出 CSV"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5v5h5v4zm-8.5 4.5H8l-1-1-1 1H4.5l2-2-2-2H6l1 1 1-1h1.5l-2 2 2 2zm3.5.5c-1.1 0-2-.9-2-2h1.5a.5.5 0 1 0 1 0c0-.3-.2-.5-.6-.7l-.4-.1c-1-.3-1.5-.9-1.5-1.7 0-1.1.9-2 2-2s2 .9 2 2h-1.5a.5.5 0 1 0-1 0c0 .2.2 .4 .6 .6l.4 .1c1 .3 1.5 1 1.5 1.8 0 1.1-.9 2-2 2zm4 .5-1.8-5H16l2 6h1l2-6h-1.2L18.5 18z"/></svg></button>
          <button class="icon-btn" :disabled="running" @click="exportExcel" title="导出 Excel"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 2H8a2 2 0 0 0-2 2v3h2V4h11v16H8v-3H6v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM5 7H3l3.5 5L3 17h2l2-3.6L10 17h2L8.5 12 12 7H10L7.5 10.6 5 7z"/></svg></button>
        </div>
        <!-- 关闭确认：Element 优先，必要时回退到自定义弹窗（以防样式/层级异常） -->
        <!-- 回退用的自定义弹窗先移除，确保优先体验 Element 样式 -->
        <!-- 头部已放置大图标，这里移除重复渲染 -->
        <div v-show="!isObjectActive" class="editor-wrap" ref="editorWrapRef" :style="{ height: editorHeight + 'px', marginTop: '0px' }" style="grid-column:1; grid-row:3; z-index:1;">
          <div class="editor" ref="editorRef" :style="{ height: editorHeight + 'px' }"></div>
        </div>
        <div v-show="!isObjectActive" class="hsplit" @mousedown="startHDrag" style="grid-column:1; grid-row:4;"></div>
        <div v-show="!isObjectActive" class="result" style="grid-column:1; grid-row:5;">
          <div class="rbody" :class="{ 'table-mode': result && result.type==='table' }">
            <div v-if="result && result.type==='table'" class="table-holder">
              <ResultTable />
            </div>
            <pre v-else-if="result && result.type==='text'" class="txt">{{ result.text }}</pre>
            <div v-else class="info muted placeholder">在此显示查询结果或执行信息</div>
          </div>
          <!-- 底部横向滚动条改为使用 ResultTable 内部自带横向滚动 -->
          <div class="x-scroll" ref="xScrollRef" v-if="false"></div>
          <div class="tq-pagination" v-if="result && result.type==='table'">
            <button class="icon-btn" :disabled="page<=1" @click="goToPage(page-1)" title="上一页">‹</button>
            <span class="muted">第</span>
            <input type="number" v-model.number="pageInput" @keyup.enter="handlePageJump" min="1" :max="totalPages" style="width:70px;height:28px" />
            <span class="muted">/ {{ totalPages }} 页</span>
            <button class="icon-btn" :disabled="page>=totalPages" @click="goToPage(page+1)" title="下一页">›</button>
            <span class="muted" style="margin-left:12px">每页</span>
            <select :value="pageSize" @change="handlePageSizeChange($event)" title="每页条数">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="muted">条，共 {{ totalRows || 0 }} 条</span>
          </div>
        </div>
        <!-- 对象浏览视图（表/视图/函数等）：占用编辑器+结果区域 -->
        <div v-show="isObjectActive" class="object-view" style="grid-column:1; grid-row:3 / 6;">
          <div class="ov-toolbar">
            <div class="title">{{ objectTabTitle }}</div>
            <div class="sp"></div>
            <input class="ov-search" v-model.trim="objectSearch" placeholder="搜索对象" />
          </div>
          <div class="ov-body">
            <div class="ov-list">
              <div
                v-for="name in filteredObjectList"
                :key="name"
                class="ov-item"
                :class="{active: name===objectSelected}"
                @click="selectObject(name)"
              >
                <span class="name">{{ name }}</span>
              </div>
              <div v-if="!objectLoading && filteredObjectList.length===0" class="muted" style="padding:8px">无对象</div>
              <div v-if="objectLoading" class="muted" style="padding:8px">加载中...</div>
            </div>
            <div class="ov-detail">
              <div class="ov-tabs">
                <button :class="{active: ovTab==='ddl'}" @click="ovTab='ddl'">DDL</button>
                <button :class="{active: ovTab==='meta'}" @click="ovTab='meta'">元数据</button>
              </div>
              <div class="ov-panel" v-if="ovTab==='ddl'">
                <div v-if="!objectSelected" class="ddl muted">请选择对象</div>
                <div v-else-if="!ovDDL" class="ddl muted">加载中...</div>
                <div v-else class="ddl cm-ddl" ref="ovDDLRef"></div>
              </div>
              <div class="ov-panel" v-else>
                <div v-if="!objectSelected" class="muted" style="padding:8px">请选择对象</div>
                <div v-else class="meta">
                  <div class="row" v-for="(v,k) in ovMeta" :key="String(k)">
                    <span class="k">{{ k }}</span>
                    <span class="v">{{ v }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 右侧对象查看器（默认隐藏，网格列2，覆盖编辑器+结果高度） -->
        <aside class="inspector" :style="{ display: inspectorVisible ? 'flex' : 'none', gridColumn: 2, gridRow: '1 / 6' }">
          <div class="inspector-tabs">
            <button class="icon-btn" :class="{active: inspectorTab==='ddl'}" title="DDL（结构）" @click="inspectorTab='ddl'">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 5h16v2H4V5zm0 6h16v2H4v-2zm0 6h10v2H4v-2z"/></svg>
            </button>
            <button class="icon-btn" :class="{active: inspectorTab==='meta'}" title="元数据" @click="inspectorTab='meta'">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h14v2H7V5zm0 6h14v2H7v-2zm0 6h14v2H7v-2zM3 5h2v2H3V5zm0 6h2v2H3v-2zm0 6h2v2H3v-2z"/></svg>
            </button>
            <div class="sp"></div>
            <button class="icon-btn close" title="关闭" @click="()=>{ inspectorVisible=false }">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.3 5.71 12 12.01l-6.3-6.3-1.4 1.41 6.29 6.29-6.29 6.3 1.4 1.41 6.3-6.3 6.29 6.3 1.41-1.41-6.3-6.3 6.3-6.29z"/></svg>
            </button>
          </div>
          <div class="inspector-body" v-if="inspectorTab==='ddl'">
            <div v-if="!inspectorDDL" class="ddl muted">加载中...</div>
            <div v-else class="ddl cm-ddl" ref="inspDDLRef"></div>
          </div>
          <div class="inspector-body" v-else>
            <div class="meta-item" v-for="(v,k) in inspectorMeta" :key="String(k)"><span class="k">{{ k }}</span><span class="v">{{ v }}</span></div>
          </div>
        </aside>
        <!-- 垂直拖动条：用于调整对象查看器宽度（位于两列之间） -->
        <div v-show="inspectorVisible" class="insp-resizer" title="拖动调整对象窗口宽度" @mousedown="startInspectorResize" style="grid-column:2; grid-row:1 / 6;"></div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUpdated, onBeforeUnmount, provide, nextTick, watchEffect } from 'vue'
import api from '../../api'
import SqlTabs from './SqlTabs.vue'
import ResultTable from './ResultTable.vue'
import ConfirmDialog from '../conn/ConfirmDialog.vue'
// CodeMirror（与旧页一致的依赖）
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, highlightActiveLine, lineNumbers } from '@codemirror/view'
import { sql, MySQL } from '@codemirror/lang-sql'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'
import { autocompletion, CompletionContext, completionKeymap, startCompletion } from '@codemirror/autocomplete'

// URL 参数（与旧独立页一致）
const sp = new URLSearchParams(window.location.search)
const raw = sp.get('connId') || sp.get('connectionId') || sp.get('conn_id') || ''
const connId = computed(() => { const n = Number(raw); return Number.isFinite(n)&&n>0 ? n : raw })
const initDb = computed(()=> sp.get('database') || sp.get('db') || sp.get('schema') || '')

// 头部连接信息
const connInfo = ref('')

// 左侧三层树状态
const instances = ref<any[]>([])
const expandConn = reactive<Record<string|number, boolean>>({})
const expandDbByConn = reactive<Record<string|number, Record<string, boolean>>>({})
const dbsByConn = reactive<Record<string|number, string[]>>({})
const tablesByKey = reactive<Record<string, string[]>>({})
const tablesLoading = reactive<Record<string, boolean>>({})
const selectedDbByConn = reactive<Record<string|number, Set<string>>>({})
// 数据库内分类展开状态：tables/views/functions/procedures/events
const dbCatOpen = reactive<Record<string, Record<string, Record<string, boolean>>>>({}) // dbCatOpen[connId][db][cat] = bool
function isDbCatOpen(id:any, db:string, cat:string){ return !!dbCatOpen[id]?.[db]?.[cat] }
function toggleDbCategory(id:any, db:string, cat:string){ if (!dbCatOpen[id]) dbCatOpen[id] = {}; if (!dbCatOpen[id][db]) dbCatOpen[id][db] = {}; dbCatOpen[id][db][cat] = !dbCatOpen[id][db][cat] }

// 列展开与缓存
const openCols = reactive<Record<string, boolean>>({}) // key: connId::db::table
const colsCache = reactive<Record<string, string[]>>({})
const colsLoading = reactive<Record<string, boolean>>({})
function colKey(id:any, db:string, tbl:string){ return `${id}::${db}::${tbl}` }
function isColumnsOpen(id:any, db:string, tbl:string){ return !!openCols[colKey(id,db,tbl)] }
function isColsLoading(id:any, db:string, tbl:string){ return !!colsLoading[colKey(id,db,tbl)] }
function getColumns(id:any, db:string, tbl:string){ return colsCache[colKey(id,db,tbl)] || [] }
// 索引展开/缓存
const openIdx = reactive<Record<string, boolean>>({})
const idxCache = reactive<Record<string, string[]>>({})
const idxLoading = reactive<Record<string, boolean>>({})
function idxKey(id:any, db:string, tbl:string){ return `${id}::${db}::${tbl}` }
function isIndexesOpen(id:any, db:string, tbl:string){ return !!openIdx[idxKey(id,db,tbl)] }
function isIdxLoading(id:any, db:string, tbl:string){ return !!idxLoading[idxKey(id,db,tbl)] }
function getIndexes(id:any, db:string, tbl:string){ return idxCache[idxKey(id,db,tbl)] || [] }
async function toggleTableIndexes(id:any, db:string, tbl:string){
  const k = idxKey(id,db,tbl)
  openIdx[k] = !openIdx[k]
  if (openIdx[k] && !(idxCache[k] && idxCache[k].length)) {
    idxLoading[k] = true
    try {
      // 新后端接口：/ticket/indexes 返回索引名数组
      let names: string[] = []
      try {
        const { data } = await api.get('/ticket/indexes', { params: { connId: id, db, database: db, schema: db, table: tbl } })
        if (Array.isArray(data)) names = data
        else if (Array.isArray((data as any)?.indexes)) names = (data as any).indexes
      } catch {}
      // 若没有接口或失败，回退为空数组（不报错，用户体验更顺滑）
      idxCache[k] = Array.from(new Set((names || []).map((n:any)=> String(n)).filter(Boolean)))
    } catch { idxCache[k] = idxCache[k] || [] }
    finally { idxLoading[k] = false }
  }
}

// 主键列缓存
const pkCache = reactive<Record<string, string[]>>({})
async function ensurePrimaryColumns(id:any, db:string, tbl:string){
  const k = idxKey(id,db,tbl)
  if (pkCache[k]) return
  try {
    const { data } = await api.get('/ticket/primary-columns', { params: { connId: id, db, database: db, schema: db, table: tbl } })
    pkCache[k] = Array.isArray(data) ? data.map((x:any)=>String(x)) : []
  } catch { pkCache[k] = [] }
}
function isPrimaryKey(id:any, db:string, tbl:string, col:string){
  const k = idxKey(id,db,tbl)
  const arr = pkCache[k]
  return Array.isArray(arr) && arr.includes(col)
}
// 获取非主键索引名（过滤 PRIMARY）
function getNonPrimaryIndexes(id:any, db:string, tbl:string){
  const k = idxKey(id,db,tbl)
  const arr = idxCache[k] || []
  return arr.filter(n => String(n).toUpperCase() !== 'PRIMARY')
}

// 快捷：插入当前表的 SELECT 示例
function insertQuickQuery(db:string, tbl:string){
  try {
    const snip = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;\n`
    if (cmView) {
      const doc = cmView.state.doc.toString()
      const prefix = (doc && !/\n$/.test(doc)) ? '\n' : ''
      cmView.dispatch({ changes: { from: doc.length, to: doc.length, insert: prefix + snip } })
      ;(globalThis as any).__next_sql_text = cmView.state.doc.toString()
      cmView.focus()
      // 确保编辑器在栅格中的行不被对象面板覆盖
      try { editorWrapRef.value?.scrollIntoView?.({ block: 'nearest' }) } catch {}
    }
  } catch {}
}

// 打开对象查看器
const inspectorLast = ref<{ id:any; db:string; tbl:string }|null>(null)
async function openInspector(id:any, db:string, tbl:string){
  inspectorVisible.value = true
  inspectorLast.value = { id, db, tbl }
  inspectorTab.value = 'ddl'
  inspectorTitle.value = `${db}.${tbl}`
  inspectorDDL.value = '加载中...'
  for (const k in inspectorMeta) delete (inspectorMeta as any)[k]
  try {
    const [{ data: ddl }, { data: meta }] = await Promise.all([
      api.get('/ticket/ddl', { params: { connId: id, db: db, database: db, table: tbl } }),
      api.get('/ticket/table-status', { params: { connId: id, db: db, database: db, table: tbl } }),
    ])
    inspectorDDL.value = typeof ddl === 'string' ? ddl : JSON.stringify(ddl, null, 2)
    // 渲染高亮
    nextTick(() => {
      try {
        const host = inspDDLRef.value
        if (host) {
          host.innerHTML = ''
          if (inspDDLView) { try { inspDDLView.destroy() } catch {} inspDDLView = null }
          inspDDLView = new EditorView({
            parent: host,
            state: EditorState.create({
              doc: inspectorDDL.value || '',
              extensions: [sql({ dialect: MySQL }), syntaxHighlighting(defaultHighlightStyle), EditorView.editable.of(false)]
            })
          })
        }
      } catch {}
    })
    Object.assign(inspectorMeta, meta || {})
  } catch (e:any) {
    inspectorDDL.value = e?.response?.data?.detail || e?.message || '加载失败'
  }
}
// 表级展开状态
const tableOpen = reactive<Record<string, boolean>>({})
function tableKey(id:any, db:string, tbl:string){ return `${id}::${db}::${tbl}` }
function isTableOpen(id:any, db:string, tbl:string){ return !!tableOpen[tableKey(id,db,tbl)] }
function toggleTableCats(id:any, db:string, tbl:string){ tableOpen[tableKey(id,db,tbl)] = !tableOpen[tableKey(id,db,tbl)] }
async function toggleTableColumns(id:any, db:string, tbl:string){
  const k = colKey(id,db,tbl)
  openCols[k] = !openCols[k]
  if (openCols[k] && !(colsCache[k] && colsCache[k].length)) {
    colsLoading[k] = true
    try {
      // 走现有列接口（兼容回退 URL）
      const params = { connId: id, db, database: db, schema: db, table: tbl, tableName: tbl, tbl }
      const { data } = await api.get('/ticket/columns', { params })
      let cols: string[] = []
      if (Array.isArray(data)) cols = data
      else if (Array.isArray((data as any)?.columns)) cols = (data as any).columns
      colsCache[k] = Array.from(new Set((cols || []).map((c:any)=> typeof c==='string'?c:(c?.name||c?.COLUMN_NAME||c?.column||c?.field||'')).filter(Boolean)))
    } catch { colsCache[k] = colsCache[k] || [] }
    finally { colsLoading[k] = false }
  }
}
const instFilterVisible = ref<string|number>('')
const instPanelPos = reactive<{left:number;top:number}>({ left: 0, top: 0 })
const instSearch = ref('')
function hasInstFilter(id:any){ const set = selectedDbByConn[id]; return !!(set && set.size>0) }
const globalDbSearch = ref('')
const hoverInst = ref<string|number>('')
const hoverDb = ref<string>('')
// 数据库过滤交互：每个库独立的过滤文本与显示状态
const dbFilterTextByKey = reactive<Record<string, string>>({})
const dbFilterVisibleKey = ref<string>('')
// 浮动输入框定位数据
const dbFilterPopup = reactive<{ show:boolean; left:number; top:number; key:string }>({ show:false, left:0, top:0, key:'' })
const popupHover = ref(false)
const leftWidth = ref(270)

// 右侧
const editorWrapRef = ref<HTMLElement|null>(null)
const editorRef = ref<HTMLElement|null>(null)
let cmView: any = null
const inspDDLRef = ref<HTMLElement|null>(null)
const ovDDLRef = ref<HTMLElement|null>(null)
let inspDDLView: any = null
let ovDDLView: any = null
const running = ref(false)
let currentAbort: AbortController | null = null
const result = ref<any|null>(null)
const currentDb = ref('')
// 每标签的上下文：连接与数据库
type TabCtx = { connId: any; database: string }
const tabCtx = reactive<Record<string, TabCtx>>({})
// 活动标签对应的下拉值（双向绑定）
const activeConnId = computed({
  get(){
    const t = tabs.find(x=>x.id===activeTab.value)
    const ctx = t ? tabCtx[t.id] : null
    return ctx ? ctx.connId : (connId.value as any)
  },
  set(v:any){
    const t = tabs.find(x=>x.id===activeTab.value)
    if (!t) return
    if (!tabCtx[t.id]) tabCtx[t.id] = { connId: v, database: '' }
    else tabCtx[t.id].connId = v
    // 动态加载对应实例的数据库
    loadDatabasesByConn(v)
  }
})
const activeDatabase = computed({
  get(){
    const t = tabs.find(x=>x.id===activeTab.value)
    const ctx = t ? tabCtx[t.id] : null
    return ctx ? ctx.database : (currentDb.value || '')
  },
  set(v:string){
    const t = tabs.find(x=>x.id===activeTab.value)
    if (!t) return
    if (!tabCtx[t.id]) tabCtx[t.id] = { connId: activeConnId.value, database: v }
    else tabCtx[t.id].database = v
    currentDb.value = v
  }
})
const editorHeight = ref(150)
const editorHeightCommitted = ref(150)
const toolbarActionsRef = ref<HTMLElement | null>(null)
let toolbarObserver: MutationObserver | null = null
let toolbarObservedEl: HTMLElement | null = null
// 对象查看器状态
const inspectorVisible = ref(false)
const inspectorTab = ref<'ddl'|'meta'>('ddl')
const inspectorDDL = ref('')
const inspectorMeta = reactive<Record<string, any>>({})
const inspectorTitle = ref('')
const inspectorWidth = ref(360)
// 对象视图状态
const objectMode = ref<'none'|'tables'|'views'|'functions'|'procedures'|'events'|'triggers'>('none')
const isObjectActive = computed(()=> objectMode.value !== 'none')
const objectTabTitle = computed(()=>{
  const map:any = { tables:'对象：表', views:'对象：视图', functions:'对象：函数', procedures:'对象：过程', events:'对象：事件', triggers:'对象：触发器' }
  return map[objectMode.value] || '对象'
})
const objectList = ref<string[]>([])
const objectLoading = ref(false)
const objectSelected = ref('')
const objectSearch = ref('')
const ovTab = ref<'ddl'|'meta'>('ddl')
const ovDDL = ref('')
const ovMeta = reactive<Record<string, any>>({})

function filtered(list:string[]): string[] { const q=(objectSearch.value||'').trim().toLowerCase(); if(!q) return list; return list.filter(n=>String(n).toLowerCase().includes(q)) }
const filteredObjectList = computed(()=> filtered(objectList.value))

async function openObjectTab(kind: typeof objectMode.value){
  objectMode.value = kind
  ovTab.value = 'ddl'
  objectSelected.value = ''
  ovDDL.value = ''
  for (const k in ovMeta) delete (ovMeta as any)[k]
  await loadObjectList()
}

async function loadObjectList(){
  objectLoading.value = true
  objectList.value = []
  try{
    const db = activeDatabase.value || currentDb.value || ''
    if (!db) { objectLoading.value=false; return }
    if (objectMode.value==='tables'){
      // 复用已有接口
      try{
        const {data}=await api.get(`/connections/${activeConnId.value}/databases/${encodeURIComponent(db)}/tables`)
        objectList.value = Array.isArray(data)?data:[]
      }catch{
        const {data}=await api.get('/ticket/tables', { params: { connId: activeConnId.value, database: db, db, schema: db } })
        objectList.value = Array.isArray(data)?data:[]
      }
    } else {
      // 其他对象后续扩展，这里先置空
      objectList.value = []
    }
  }catch{ objectList.value=[] }
  finally{ objectLoading.value=false }
}

async function selectObject(name:string){
  objectSelected.value = name
  ovTab.value = 'ddl'
  ovDDL.value = '加载中...'
  for (const k in ovMeta) delete (ovMeta as any)[k]
  try{
    const db = activeDatabase.value || currentDb.value || ''
    const [{data: ddl}, {data: meta}] = await Promise.all([
      api.get('/ticket/ddl', { params: { connId: activeConnId.value, database: db, db, table: name } }),
      api.get('/ticket/table-status', { params: { connId: activeConnId.value, database: db, db, table: name } })
    ])
    ovDDL.value = typeof ddl==='string'?ddl:JSON.stringify(ddl,null,2)
    // 渲染高亮
    nextTick(() => {
      try {
        const host = ovDDLRef.value
        if (host) {
          host.innerHTML = ''
          if (ovDDLView) { try { ovDDLView.destroy() } catch {} ovDDLView = null }
          ovDDLView = new EditorView({
            parent: host,
            state: EditorState.create({
              doc: ovDDL.value || '',
              extensions: [sql({ dialect: MySQL }), syntaxHighlighting(defaultHighlightStyle), EditorView.editable.of(false)]
            })
          })
        }
      } catch {}
    })
    Object.assign(ovMeta, meta||{})
  }catch(e:any){ ovDDL.value = e?.response?.data?.detail || e?.message || '加载失败' }
}
function startInspectorResize(e: MouseEvent){
  const startX = e.clientX
  const startW = inspectorWidth.value
  const onMove = (ev: MouseEvent) => {
    const dx = ev.clientX - startX
    inspectorWidth.value = Math.max(260, Math.min(800, startW - dx))
  }
  const onUp = () => {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp, { once: true })
}
let editorResizeObserver: ResizeObserver | null = null

function setupToolbarObserver(){
  try {
    const target = toolbarActionsRef.value
    if (!target) return
    if (!toolbarObserver) {
      toolbarObserver = new MutationObserver(() => {
        try {
          target.classList.add('sticky')
          target.style.visibility = 'visible'
          target.style.opacity = '1'
          target.style.pointerEvents = 'auto'
        } catch {}
      })
    }
    if (toolbarObservedEl !== target) {
      toolbarObserver.disconnect()
      toolbarObservedEl = target
      target.classList.add('sticky')
      target.style.visibility = 'visible'
      target.style.opacity = '1'
      target.style.pointerEvents = 'auto'
      toolbarObserver.observe(target, { attributes: true, attributeFilter: ['style'], attributeOldValue: true })
    }
  } catch {}
}

onBeforeUnmount(() => {
  if (toolbarObserver) {
    toolbarObserver.disconnect()
    toolbarObservedEl = null
  }
})

// 结果与分页
const page = ref(1)
const pageSize = ref(50)
const totalRows = ref(0)
const pageInput = ref(1)
const totalPages = computed(()=>{ const t=Number(totalRows.value||0); const ps=Number(pageSize.value||1); return Math.max(1, Math.ceil(t/Math.max(1,ps))) })

// ResultTable 上下文（与旧页一致的头部锁定/排序/同步滚动逻辑）
const tq = reactive<any>({
  result: computed(()=> result.value),
  tableColWidths: [] as number[],
  bodyTableWidth: 0,
  freezeCount: 0,
  freezeLefts: [] as number[],
  sortKey: '',
  sortDir: 'asc',
  page,
  pageSize,
  isRunning: computed(()=> running.value),
  qTabs: [] as any[],
  activeQueryTabId: '' as any
})
const tqHeadTableRef = ref<any>(null)
const tqBodyTableRef = ref<any>(null)
const tqScrollXRef = ref<any>(null)
const tqBodyRef = ref<any>(null)
const xScrollRef = ref<HTMLElement|null>(null)
const bodyScrollRef = ref<HTMLElement|null>(null)
const spacerWidth = ref(1600)

function updateSpacerWidth(){
  try {
    const bodyTable = tqBodyTableRef.value as HTMLTableElement | null
    const body = tqBodyRef.value as HTMLElement | null
    const widthFromDom = bodyTable ? bodyTable.scrollWidth : 0
    const widthFromBody = body ? body.scrollWidth : 0
    const computedCols = tq.tableColWidths.reduce((a: number, b: number) => a + b, 0)
    const finalWidth = Math.max(widthFromDom, widthFromBody, computedCols, 1600)
    spacerWidth.value = finalWidth
    tq.bodyTableWidth = finalWidth
    // 始终显示底部横向滚动条由 CSS 控制；这里不再强制隐藏
  } catch {
    const fallback = Math.max(tq.bodyTableWidth || 0, 1600)
    spacerWidth.value = fallback
    tq.bodyTableWidth = fallback
  }
  try {
    const wrap = editorWrapRef.value
    if (wrap) {
      wrap.style.overflow = 'visible'
      wrap.style.position = 'relative'
    }
  } catch {}
}

/**
 * 计算结果表格的每列宽度（带中文注释）
 * - 优先依据第一行数据单元格的实际宽度
 * - 再叠加表头文本的滚动宽度，保证"列标题完整可见"，不被截断
 * - 取两者更大值作为该列最终宽度
 */
function computeColWidths(){
  try {
    const bodyTable = tqBodyTableRef.value as HTMLTableElement | null
    const headTable = tqHeadTableRef.value as HTMLTableElement | null
    const colCount = (result.value?.columns || []).length
    let widths: number[] = []

    if (!bodyTable) {
      widths = (result.value?.columns || []).map(() => 140)
    } else {
      const firstRowCells = Array.from(bodyTable.querySelectorAll('tbody tr:first-child td')) as HTMLElement[]
      if (firstRowCells.length) {
        widths = firstRowCells.map((cell: any) => Math.max(120, Math.ceil(Number(cell?.offsetWidth || cell?.clientWidth || 120))))
      } else {
        widths = (result.value?.columns || []).map(() => 140)
      }
    }

    // 叠加表头文本实际所需宽度，保证标题不被截断
    try {
      if (headTable && colCount) {
        const ths = Array.from(headTable.querySelectorAll('thead th')) as HTMLElement[]
        for (let i = 0; i < colCount; i++) {
          const th = ths[i] as HTMLElement | undefined
          if (!th) continue
          const inner = th.querySelector('.th-inner') as HTMLElement | null
          const need = Math.ceil(Number(inner?.scrollWidth || th.scrollWidth || 0)) + 20 // 文本+操作按钮+resizer 余量
          widths[i] = Math.max(widths[i] || 120, Math.max(120, need))
        }
      }
    } catch {}

    tq.tableColWidths = widths
    tq.bodyTableWidth = widths.reduce((a: number, b: number) => a + b, 0)
  } catch {
    const cols = (result.value?.columns || []).map(() => 140)
    tq.tableColWidths = cols
    tq.bodyTableWidth = cols.reduce((a, b) => a + b, 0)
  }
  nextTick(() => {
    updateSpacerWidth()
    syncHorizontalScroll()
  })
}
function adjustHeaderGutter(){ /* 已在子组件内处理 */ }
function getDisplayedRows(){ try{ const rows = (result.value?.data)||[]; const start=(page.value-1)*pageSize.value; return rows.slice(start, start+pageSize.value) } catch { return [] } }
function headerLockClick(i:number){ tq.freezeCount = (i < tq.freezeCount) ? i : (i+1) ; const lefts:number[]=[]; let acc=0; for(let k=0;k<tq.freezeCount;k++){ acc += Number(tq.tableColWidths[k]||0); lefts[k]=acc-Number(tq.tableColWidths[k]||0) } tq.freezeLefts = lefts }
function toggleSort(col:string){ if (tq.sortKey===col) { tq.sortDir = tq.sortDir==='asc'?'desc':'asc' } else { tq.sortKey=col; tq.sortDir='asc' } try { const rows = (result.value?.data)||[]; const dir = tq.sortDir==='asc'?1:-1; const sorted = [...rows].sort((a:any,b:any)=> (a?.[col] > b?.[col] ? dir : -dir)); result.value = { ...result.value, data: sorted } } catch {} }
function startColResize(i:number, e:MouseEvent){ const startX=e.clientX; const startW = Number(tq.tableColWidths[i]||140); const onMove=(ev:MouseEvent)=>{ const w=Math.max(80, startW + ev.clientX - startX); tq.tableColWidths.splice(i,1,w); tq.bodyTableWidth = tq.tableColWidths.reduce((a:number,b:number)=>a+b,0) }; const onUp=()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }
function onBodyScroll(ev?: Event){
  try {
    const body = (ev?.target as HTMLElement) || (tqBodyRef.value as HTMLElement | null)
    if (!body) return
    syncHorizontalScroll(body.scrollLeft)
    syncBodyScroll(body.scrollTop)
    updateSpacerWidth()
  } catch {}
}

function resetTableScroll(){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    if (body) {
      body.scrollTop = 0
    }
  } catch {}
  syncHorizontalScroll(0)
  syncBodyScroll(0)
  updateSpacerWidth()
}

function syncBodyScroll(targetTop?: number){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    const ext = bodyScrollRef.value as HTMLElement | null
    if (!body || !ext) return
    const top = typeof targetTop === 'number' ? targetTop : body.scrollTop
    if (typeof targetTop === 'number' && body.scrollTop !== targetTop) body.scrollTop = targetTop
    if (ext.scrollTop !== top) ext.scrollTop = top
  } catch {}
}

function syncHorizontalScroll(targetLeft?: number){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    const xs = null as any // 不再同步到外部 x-scroll，使用内部横向滚动条
    const head = tqScrollXRef.value as HTMLElement | null
    const left = typeof targetLeft === 'number' ? targetLeft : Number(body?.scrollLeft || 0)
    if (typeof targetLeft === 'number' && body && body.scrollLeft !== targetLeft) body.scrollLeft = targetLeft
    // 移除 xs 同步
    if (head && head.scrollLeft !== left) head.scrollLeft = left
  } catch {}
}

provide('tqCtx', {
  tq,
  tqHeadTableRef,
  tqBodyTableRef,
  tqScrollXRef,
  tqBodyRef,
  bodyScrollRef,
  editorWrapRef,
  computeColWidths,
  adjustHeaderGutter,
  getDisplayedRows,
  headerLockClick,
  toggleSort,
  startColResize,
  onBodyScroll,
  resetTableScroll,
  // 供 SqlTabs 使用（与独立窗口保持一致的方法名）
  newQueryTab: () => newTab(),
  closeQueryTab: (id: string) => requestCloseTab(id),
  activateQueryTab: (id: string) => switchTab(id)
})

function toggleConn(id:any){ expandConn[id] = !expandConn[id]; if (expandConn[id] && !dbsByConn[id]) loadDatabasesByConn(id) }
function toggleDb(id:any, db:string){ if (!expandDbByConn[id]) expandDbByConn[id] = {}; expandDbByConn[id][db] = !expandDbByConn[id][db]; if (expandDbByConn[id][db]) { currentDb.value = db; loadTablesByConnDb(id, db) } }

function openInstFilter(inst:any, ev?: MouseEvent){
  instFilterVisible.value = inst.id
  if (!dbsByConn[inst.id]) loadDatabasesByConn(inst.id)
  if (!selectedDbByConn[inst.id]) selectedDbByConn[inst.id] = new Set<string>()
  try {
    const btn = ev?.currentTarget as HTMLElement | null
    if (btn) {
      const rect = btn.getBoundingClientRect()
      // 与按钮同水平位置显示（靠近右侧，向下 4px）
      instPanelPos.left = rect.right + 8
      instPanelPos.top = rect.top + window.scrollY + 4
    } else {
      instPanelPos.left = leftWidth.value + 12
      instPanelPos.top = 0
    }
  } catch {}
  nextTick(()=>{
    try {
      const input = document.querySelector('.inst-panel .ph-search input') as HTMLInputElement | null
      input && input.focus()
    } catch {}
  })
}
function filterInstDbs(id:any){
  const kw = (instSearch.value||'').trim().toLowerCase()
  const all = dbsByConn[id] || []
  if (!kw) return all
  return all.filter((n:string)=> n.toLowerCase().includes(kw))
}
function isDbSelected(id:any, db:string){ return !!selectedDbByConn[id]?.has(db) }
function onDbSelect(id:any, db:string, ev:Event){ const on=(ev.target as HTMLInputElement).checked; if(!selectedDbByConn[id]) selectedDbByConn[id]=new Set<string>(); if(on) selectedDbByConn[id].add(db); else selectedDbByConn[id].delete(db) }
function filteredDbList(id:any){ const all = dbsByConn[id]||[]; const sel=selectedDbByConn[id]; const tokens=(globalDbSearch.value||'').trim().toLowerCase().split(/\s+/).filter(Boolean); return all.filter(db=>{ if(sel&&sel.size>0&&!sel.has(db)) return false; if(!tokens.length) return true; const s=db.toLowerCase(); return tokens.some(t=>s.includes(t)) }) }
// 保留旧方法名：为了兼容引用，如有调用则改为展示浮层
function openDbFilter(id:any, db:string){ showDbFilterPopup(id, db) }
// 改为行内输入：显示输入框并保持图标可见
function keyOf(id:any, db:string){ return `${id}::${db}` }
function openDbFilterInline(id:any, db:string){ dbFilterVisibleKey.value = keyOf(id, db) }
// 打开浮动输入框：根据按钮位置计算坐标，让其可跨出左栏
function showDbFilterPopup(id:any, db:string, ev?: MouseEvent){
  const key = keyOf(id, db)
  dbFilterVisibleKey.value = key
  try {
    const btn = ev?.currentTarget as HTMLElement | null
    if (btn) {
      const rect = btn.getBoundingClientRect()
      dbFilterPopup.show = true
      dbFilterPopup.left = rect.right + 8 // 在按钮右侧 8px
      dbFilterPopup.top = rect.top - 2
      dbFilterPopup.key = key
      popupInputValue.value = dbFilterTextByKey[key] || ''
      nextTick(() => {
        const el = document.querySelector('.db-filter-float') as HTMLInputElement | null
        try { el && el.focus() } catch {}
      })
    }
  } catch {}
}
const popupInputValue = ref('')
function onPopupInput(e: Event){ popupInputValue.value = (e.target as HTMLInputElement).value }
function onPopupChange(){ dbFilterTextByKey[dbFilterPopup.key] = popupInputValue.value.trim(); if(!dbFilterTextByKey[dbFilterPopup.key]) { dbFilterPopup.show=false; dbFilterVisibleKey.value=''} }
function onPopupConfirm(){
  // 提交并展开当前库
  dbFilterTextByKey[dbFilterPopup.key] = (popupInputValue.value || '').trim()
  // 解析 key -> id,db
  try {
    const [idStr, db] = dbFilterPopup.key.split('::')
    const id:any = isNaN(Number(idStr)) ? idStr : Number(idStr)
    if (!expandDbByConn[id]) expandDbByConn[id] = {}
    expandDbByConn[id][db] = true
  } catch {}
  // 关闭浮窗
  dbFilterPopup.show = false
}
function onDbFilterInput(id:any, db:string, e:Event){
  const key = keyOf(id, db)
  const txt = String((e.target as HTMLInputElement)?.value || '').trim()
  dbFilterTextByKey[key] = txt
  const all = tablesByKey[key] || []
  if (!txt) { // 恢复原始（若无缓存则保持）
    // 不改 tablesByKey，本地显示时用 filteredTablesFor 结合文本过滤
  }
}
function onDbMouseLeave(id:any, db:string){
  const key = keyOf(id, db)
  hoverDb.value = ''
  // 若无过滤文本则隐藏输入框和图标（允许鼠标移至浮窗时不立即关闭）
  if (!dbFilterTextByKey[key]) {
    dbFilterVisibleKey.value = ''
    setTimeout(() => {
      if (!popupHover.value && (!dbFilterPopup.key || !dbFilterTextByKey[dbFilterPopup.key])) {
        dbFilterPopup.show = false
      }
    }, 120)
  }
}
function clearInstSelected(id:any){ if (selectedDbByConn[id]) selectedDbByConn[id].clear() }
function filteredTablesFor(id:any, db:string){ const key=`${id}::${db}`; return tablesByKey[key]||[] }
// 增强：若存在过滤文本，则基于缓存结果做一次前端过滤
function filteredTablesForDisplay(id:any, db:string){
  const key = keyOf(id, db)
  const base = tablesByKey[key] || []
  const txt = (dbFilterTextByKey[key] || '').toLowerCase().trim()
  if (!txt) return base
  const tokens = txt.split(/\s+/).filter(Boolean)
  if (!tokens.length) return base
  return base.filter(t => tokens.some(k => String(t).toLowerCase().includes(k)))
}
function clearAllDbFilters(){
  // 清除所有库的过滤文本，并隐藏浮窗
  for (const k of Object.keys(dbFilterTextByKey)) delete dbFilterTextByKey[k]
  dbFilterPopup.show = false
  dbFilterVisibleKey.value = ''
  // 同时清除“实例级别的库选择过滤”（全局清理）
  try {
    for (const id in selectedDbByConn) {
      const set = selectedDbByConn[id]
      if (set && typeof set.clear === 'function') set.clear()
    }
  } catch {}
}
function collapseAllDbs(){
  // 折叠到实例级：关闭所有实例与其下数据库展开
  for (const id in expandConn) expandConn[id] = false
  for (const id in expandDbByConn) {
    const m = expandDbByConn[id]
    if (m) for (const db in m) m[db] = false
  }
  instFilterVisible.value = ''
}
function loadingKey(id:any, db:string){ return !!tablesLoading[`${id}::${db}`] }
function emptyKey(id:any, db:string){ const key=`${id}::${db}`; const arr=tablesByKey[key]; return Array.isArray(arr) && arr.length===0 }

async function loadConnections(){ try{ const {data}=await api.get('/connections'); instances.value=Array.isArray(data)?data:[] }catch{ instances.value=[] } }
async function loadConnInfo(){ try{ const {data}=await api.get(`/connections/${connId.value}`); connInfo.value = `${data.user}@${data.ip}:${data.port} (${data.description||data.ip+':'+data.port||('#'+data.id)})` }catch{ connInfo.value='' } }
async function loadDatabasesByConn(id:any){ try{ const {data}=await api.get(`/connections/${id}/databases`); dbsByConn[id]=Array.isArray(data)?data:[] }catch{ dbsByConn[id]=dbsByConn[id]||[] } }
async function loadTablesByConnDb(id:any, db:string){
  const key=`${id}::${db}`; tablesLoading[key]=true
  try{
    // 优先新接口
    try{
      const {data}=await api.get(`/connections/${id}/databases/${encodeURIComponent(db)}/tables`)
      if (Array.isArray(data)) { tablesByKey[key]=data; return }
    }catch{}
    // 回退旧接口（与现有后端兼容）
    const { data } = await api.get('/ticket/tables', { params: { connId: id, db, database: db, schema: db } })
    tablesByKey[key] = Array.isArray(data) ? data : []
  }catch{ tablesByKey[key]=tablesByKey[key]||[] }
  finally{ tablesLoading[key]=false }
}

function startDrag(e:MouseEvent){ const sx=e.clientX, sw=leftWidth.value; const onMove=(ev:MouseEvent)=>{ leftWidth.value=Math.max(180, Math.min(560, sw + ev.clientX - sx)) }; const onUp=()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp)}; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }

function startHDrag(e:MouseEvent){ const sy=e.clientY, sh=editorHeight.value; try{ document.body.style.cursor='row-resize'; document.documentElement.classList.add('no-select') }catch{}; const onMove=(ev:MouseEvent)=>{ const nh = Math.max(0, Math.min(600, sh + ev.clientY - sy)); editorHeight.value = nh; try{ cmView && cmView.requestMeasure && cmView.requestMeasure() }catch{} }; const onUp=()=>{ editorHeightCommitted.value = editorHeight.value; refreshEditorLayout(); try{ document.body.style.cursor=''; document.documentElement.classList.remove('no-select') }catch{}; window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp)}; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }

function onDragHover(ev: MouseEvent){
  try {
    const y = ev.clientY
    const rectWrap = (editorWrapRef.value as HTMLElement | null)?.getBoundingClientRect()
    if (rectWrap) {
      const barTop = rectWrap.bottom
      const near = Math.abs(y - barTop) <= 12
      document.body.style.cursor = near ? 'row-resize' : ''
    }
  } catch {}
}

function appendSnip(instId:any, db:string, tbl:string){
  currentDb.value = db
  // 将点击来源的实例/数据库保存到当前标签上下文
  try {
    const t = tabs.find(x=>x.id===activeTab.value)
    if (t) {
      tabCtx[t.id] = { connId: instId, database: db }
      // 确保数据库下拉可选
      if (!dbsByConn[instId]) loadDatabasesByConn(instId)
    }
  } catch {}
  const snip = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;\n`
  try {
    if (cmView) {
      const doc = cmView.state.doc.toString()
      const prefix = (doc && !/\n$/.test(doc)) ? '\n' : ''
      cmView.dispatch({ changes: { from: doc.length, to: doc.length, insert: prefix + snip } })
      ;(globalThis as any).__next_sql_text = cmView.state.doc.toString()
      cmView.focus()
      return
    }
  } catch {}
}
/**
 * 执行当前标签页的 SQL
 * - 成功后会把"结果与分页状态"写回到当前标签对象，做到"每个标签互不影响"
 */
async function exec(){
  const wasInspectorVisible = inspectorVisible.value
  const txtGlobal = (globalThis as any).__next_sql_text
  const sql = (typeof txtGlobal==='string' && txtGlobal.trim()) ? txtGlobal : ''
  if(!sql) return
  // 若已有执行在进行，则直接返回，防止并发执行
  if (running.value) return
  ensureActionBarVisible()
  page.value = Math.max(1, page.value)
  running.value=true; result.value={ type:'text', text:'执行中...' }
  // 创建取消控制器
  try { if (currentAbort) currentAbort.abort() } catch {}
  currentAbort = new AbortController()
  try{
    // 使用每个标签独立的连接/数据库上下文
    const ctx = tabs.find(t=>t.id===activeTab.value) ? tabCtx[activeTab.value] : null
    const useConn = ctx?.connId ?? connId.value
    const useDb = ctx?.database || currentDb.value
    const payload:any = { connId: useConn, sql, page: page.value, pageSize: pageSize.value }
    try { if (/\blimit\b/i.test(sql)) payload.respectInnerLimit = true } catch {}
    if (useDb) payload.database = useDb
    const {data}=await api.post('/ticket/execute', payload, { signal: (currentAbort as any)?.signal })
    if (data && Array.isArray(data.data) && Array.isArray(data.columns)) {
      result.value={ type:'table', data:data.data, columns:data.columns }
      totalRows.value = Number(data.total || data.count || data.totalRows || data.data.length || 0)
      pageInput.value = page.value
    } else if (Array.isArray(data)) {
      const cols = data.length ? Object.keys(data[0]) : []
      result.value={ type:'table', data, columns: cols }
      totalRows.value = data.length
      pageInput.value = page.value
    } else if (data && Array.isArray(data.rows) && Array.isArray(data.columns)) {
      result.value={ type:'table', data:data.rows, columns:data.columns }
      totalRows.value = Number(data.total || data.count || data.rows.length || 0)
      pageInput.value = page.value
    } else if (typeof data==='string') {
      result.value={ type:'text', text:data }
    } else if (data && (data.message || data.text)) {
      result.value={ type:'text', text: data.message || data.text }
    } else {
      result.value={ type:'text', text: '执行完成' }
    }
  }catch(e:any){
    const aborted = (e && (e.name==='CanceledError' || e.name==='AbortError'))
    result.value={ type:'text', text: aborted ? '已停止执行' : (e?.response?.data?.detail || e?.message || '执行失败') }
  } finally{ running.value=false; try{ currentAbort = null }catch{} }
  await nextTick()
  computeColWidths()
  resetTableScroll()
  updateSpacerWidth()
  await refreshEditorLayout()
  // 若对象查看器之前已打开，则保持打开；必要时刷新其标题
  try {
    if (wasInspectorVisible && inspectorLast.value) {
      inspectorVisible.value = true
      inspectorTitle.value = `${inspectorLast.value.db}.${inspectorLast.value.tbl}`
    }
  } catch {}
  // 执行后保持 tabs 吸顶与层级，且编辑器紧贴其下，不允许编辑器层级超过 tabs
  try {
    const tabsEl = document.querySelector('.tabs') as HTMLElement | null
    const editorWrap = editorWrapRef.value
    if (tabsEl) { tabsEl.style.position = 'sticky'; tabsEl.style.top = '0px'; tabsEl.style.zIndex = '10000' }
    if (editorWrap) { editorWrap.style.marginTop = '0px'; editorWrap.style.zIndex = '1' }
  } catch {}
  const active = tabs.find(t => t.id === activeTab.value)
  if (active) {
    active.dirty = false
    active.result = result.value
    active.page = page.value
    active.pageSize = pageSize.value
    active.totalRows = totalRows.value
  }
  ensureActionBarVisible()
  setTimeout(() => ensureActionBarVisible(), 0)
}
function stop(){
  try { currentAbort && currentAbort.abort() } catch {}
  running.value=false
  ensureActionBarVisible()
  setTimeout(() => ensureActionBarVisible(), 0)
}
async function viewPlan(){
  try {
    const txtGlobal = (globalThis as any).__next_sql_text
    const sqlText = (typeof txtGlobal==='string' ? txtGlobal : cmView?.state?.doc?.toString() || '') || ''
    if (!sqlText.trim()) return
    // 使用每个标签的连接/数据库上下文
    const ctx = tabs.find(t=>t.id===activeTab.value) ? tabCtx[activeTab.value] : null
    const useConn = ctx?.connId ?? connId.value
    const useDb = ctx?.database || currentDb.value || ''
    result.value = { type: 'text', text: '生成执行计划中...' }
    const { data } = await api.post('/ticket/plan', { connId: useConn, database: useDb, sql: sqlText })
    if (typeof data === 'string') {
      result.value = { type: 'text', text: data }
    } else if (data && data.message) {
      result.value = { type: 'text', text: data.message }
    } else {
      result.value = { type: 'text', text: JSON.stringify(data, null, 2) }
    }
    const t = tabs.find(x=>x.id===activeTab.value); if (t) t.result = result.value
  } catch (e:any) {
    const msg = e?.response?.data?.detail || e?.message || '获取执行计划失败'
    result.value = { type: 'text', text: String(msg) }
    const t = tabs.find(x=>x.id===activeTab.value); if (t) t.result = result.value
  }
}
function beautify(){
  try{
    if(!cmView) return
    let s = cmView.state.doc.toString()
    s = s.replace(/[\t ]+/g,' ').replace(/\s*;\s*/g,';\n').replace(/\n{3,}/g,'\n\n').trim()+'\n'
    cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: s } })
    ;(globalThis as any).__next_sql_text = s
    // 同步到当前标签文本
    const t = tabs.find(x=>x.id===activeTab.value)
    if (t) { t.text = s; t.dirty = true }
    try { cmView.focus() } catch {}
  }catch{}
}

// 保留分页工具函数
function goToPage(p:number){ const tp=totalPages.value; const n=Math.min(tp, Math.max(1, Number(p)||1)); if(n===page.value) return; page.value=n; pageInput.value=n; exec() }
function handlePageJump(){ goToPage(pageInput.value as any) }
function handlePageSizeChange(e:Event){ const v=Number((e.target as HTMLSelectElement)?.value||pageSize.value); if(!Number.isFinite(v)||v<=0) return; pageSize.value=v; page.value=1; pageInput.value=1; exec() }

function onXScroll(){ /* 保留函数占位，已不使用外部 x-scroll */ }

function ensureActionBarVisible(){
  setupToolbarObserver()
  try {
    const wrap = editorWrapRef.value
    if (wrap) {
      wrap.style.position = 'relative'
      wrap.style.overflow = 'visible'
    }
  } catch {}
}

function syncEditorScrollerOverflow(){
  try {
    const host = editorRef.value as HTMLElement | null
    if (!host) return
    const scroller = host.querySelector('.cm-scroller') as HTMLElement | null
    const content = host.querySelector('.cm-content') as HTMLElement | null
    if (!scroller || !content) return
    // 启用自动折行后始终隐藏横向滚动
    scroller.style.overflowX = 'hidden'
    scroller.style.overflowY = 'auto'
  } catch {}
}

async function refreshEditorLayout(){
  if (editorHeight.value !== editorHeightCommitted.value) {
    editorHeight.value = editorHeightCommitted.value
  }
  await nextTick()
  try { cmView && cmView.requestMeasure && cmView.requestMeasure() } catch {}
  ensureActionBarVisible()
  syncEditorScrollerOverflow()
}

// 标签页
type Tab = {
  id: string
  title: string
  text: string
  dirty?: boolean
  result?: any | null
  page?: number
  pageSize?: number
  totalRows?: number
}
const tabs = reactive<Tab[]>([])
const activeTab = ref('')
// 关闭标签确认弹窗状态
const confirmCloseVisible = ref(false)
const closingTabId = ref('')
function newTab(){
  const n = tabs.length + 1
  const t:Tab = { id: String(Date.now()) + '-' + n, title: `SQL ${n}`, text: '', result: null, page: 1, pageSize: 50, totalRows: 0 }
  tabs.push(t)
  activeTab.value = t.id
  // 初始化标签上下文为当前页面的连接与数据库
  tabCtx[t.id] = { connId: connId.value, database: currentDb.value || '' }
  if (cmView) {
    cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: '' } })
    ;(globalThis as any).__next_sql_text = ''
  }
  // 重置全局呈现为该标签的状态
  result.value = null
  page.value = 1
  pageInput.value = 1
  pageSize.value = 50
  totalRows.value = 0
  refreshEditorLayout(); ensureActionBarVisible(); setTimeout(() => ensureActionBarVisible(), 0)
}
function reallyCloseTab(id:string){
  const idx = tabs.findIndex(t=>t.id===id)
  if (idx<0) return
  const wasActive = tabs[idx].id===activeTab.value
  tabs.splice(idx,1)
  if (!tabs.length) { newTab(); return }
  if (wasActive) { const next = tabs[Math.max(0, idx-1)]; switchTab(next.id) }
}
function requestCloseTab(id:string){ closingTabId.value = id; confirmCloseVisible.value = true }
function performCloseTab(){ const id = closingTabId.value; confirmCloseVisible.value = false; if (id) reallyCloseTab(id); closingTabId.value = '' }
function cancelCloseTab(){ confirmCloseVisible.value = false; closingTabId.value = '' }
function switchTab(id:string){
  const t = tabs.find(x=>x.id===id)
  if (!t) return
  activeTab.value = id
  if (cmView) {
    cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: t.text||'' } })
    ;(globalThis as any).__next_sql_text = t.text||''
    try { cmView.focus() } catch {}
  }
  // 恢复该标签自己的结果与分页
  result.value = t.result ?? null
  page.value = Number(t.page || 1)
  pageInput.value = page.value
  pageSize.value = Number(t.pageSize || 50)
  totalRows.value = Number(t.totalRows || 0)
  // 恢复该标签的连接/数据库
  try{
    const ctx = tabCtx[t.id]
    if (ctx) {
      // 触发计算属性 get 即可；需要时加载数据库
      if (ctx.connId && !dbsByConn[ctx.connId]) loadDatabasesByConn(ctx.connId)
      currentDb.value = ctx.database || ''
    }
  }catch{}
  // 刷新表格宽度与滚动
  refreshEditorLayout(); ensureActionBarVisible(); setTimeout(() => { computeColWidths(); resetTableScroll(); updateSpacerWidth(); ensureActionBarVisible(); try{ cmView && cmView.focus() }catch{}; }, 0)
}
function updateActiveTabText(txt:string){ const t = tabs.find(x=>x.id===activeTab.value); if (t) { t.text = txt; t.dirty = true } }

// 将本地 tabs 同步到 tq（供 SqlTabs 复用旧样式）
watchEffect(() => {
  tq.qTabs = tabs.map(t => ({ id: t.id, title: t.title, ui: { dirty: !!t.dirty, disabled: running.value } }))
  tq.activeQueryTabId = activeTab.value
})

// 兼容 SqlTabs 调用的方法
;(tq as any).activateQueryTab = (id:string) => switchTab(id)
;(tq as any).newQueryTab = () => newTab()
;(tq as any).closeQueryTab = (id:string) => requestCloseTab(id)

function exportCSV(){ try{ if(!result.value || result.value.type!=='table') return; const cols = result.value.columns||[]; const rows = result.value.data||[]; const esc=(s:any)=>`"${String(s??'').replace(/"/g,'""')}"`; const lines = [cols.map(esc).join(',')].concat(rows.map((r:any)=> cols.map(c=>esc(r?.[c])).join(','))); const blob = new Blob([lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' }); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='query.csv'; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 2000) } catch{} }
function exportExcel(){ try{ if(!result.value || result.value.type!=='table') return; const cols = result.value.columns||[]; const rows = result.value.data||[]; const html = `<table>${['<tr>'+cols.map(c=>`<th>${c}</th>`).join('')+'</tr>'].concat(rows.map((r:any)=>'<tr>'+cols.map(c=>`<td>${r?.[c]??''}</td>`).join('')+'</tr>')).join('')}</table>`; const blob = new Blob([`\ufeff${html}`], { type: 'application/vnd.ms-excel' }); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='query.xls'; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 2000) } catch{} }

onMounted(async()=>{ await loadConnections(); await loadConnInfo(); if (instances.value.length && connId.value) { expandConn[connId.value]=true; await loadDatabasesByConn(connId.value) } })
// ====== 挂载 CodeMirror，高亮与联想 ======
onMounted(()=>{
  const host = editorRef.value
  if (!host) return
  try {
    const keywordList = ['SELECT','FROM','WHERE','GROUP BY','ORDER BY','LIMIT','OFFSET','JOIN','LEFT JOIN','RIGHT JOIN','INNER JOIN','OUTER JOIN','ON','AND','OR','NOT','IN','IS NULL','IS NOT NULL','LIKE','BETWEEN','INSERT','INTO','VALUES','UPDATE','SET','DELETE','CREATE','TABLE','VIEW','INDEX','DROP','ALTER','ADD','PRIMARY KEY']
      .map(l=>({ label:l, type:'keyword', apply:l }))
    const columnsCache = new Map<string,string[]>()
    const columnsPending = new Set<string>()
    const getColKey = (db:string, table:string)=>`${db}.${table}`

    async function fetchTables(db:string): Promise<string[]> {
      try {
        // 先用新接口
        try {
          const { data } = await api.get(`/connections/${connId.value}/databases/${encodeURIComponent(db)}/tables`)
          if (Array.isArray(data)) return data
        } catch {}
        // 回退旧接口
        const { data } = await api.get('/ticket/tables', { params: { connId: connId.value, db, database: db, schema: db } })
        return Array.isArray(data)?data:[]
      } catch { return [] }
    }
    async function fetchColumns(db:string, table:string): Promise<string[]> {
      try {
        const key = getColKey(db, table)
        const cached = columnsCache.get(key); if (cached && cached.length) return cached
        if (columnsPending.has(key)) return []
        columnsPending.add(key)
        // 仅回退接口（与你后端兼容）
        const params = new URLSearchParams({ connId: String(connId.value||''), db, database: db, schema: db, table, tableName: table, tbl: table, format:'json' })
        let res = await fetch(`/api/ticket/columns?${params.toString()}`, { headers: { 'Accept': 'application/json' } })
        let data: any
        if (res.ok && String(res.headers.get('content-type')||'').includes('application/json')) data = await res.json()
        else {
          // 尝试文本 JSON
          const txt = await res.text(); if (txt && (txt.trim().startsWith('[')||txt.trim().startsWith('{'))) data = JSON.parse(txt)
        }
        let cols: string[] = []
        if (Array.isArray(data)) {
          if (data.length && typeof data[0]==='string') cols = data
          else {
            const keys=['name','column','column_name','COLUMN_NAME','field','Field']
            cols = (data as any[]).map(o=>{ for (const k of keys) if (o && typeof o[k]==='string') return o[k]; return '' }).filter(Boolean)
          }
        } else if (Array.isArray(data?.columns)) {
          const arr = data.columns; const keys=['name','column','column_name','COLUMN_NAME','field','Field']
          cols = (arr as any[]).map(o=>{ if (typeof o==='string') return o; for (const k of keys) if (o && typeof o[k]==='string') return o[k]; return '' }).filter(Boolean)
        }
        const uniq = Array.from(new Set(cols))
        columnsCache.set(key, uniq)
        columnsPending.delete(key)
        return uniq
      } catch { columnsPending.delete(`${db}.${table}`); return [] }
    }

    function buildDbList(): string[] { try { return dbsByConn[connId.value as any] || [] } catch { return [] } }
    function buildAliasMap(state: EditorState): Record<string,{db:string, table:string}> {
      const text = state.doc.toString()
      const alias: Record<string,{db:string, table:string}> = {}
      const reDbTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s*\.\s*([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
      const reTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
      let m: RegExpExecArray | null
      while ((m = reDbTable.exec(text))) { const db=m[2].replace(/`/g,''); const table=m[3].replace(/`/g,''); const a=m[4].replace(/`/g,'').toLowerCase(); alias[a]={db,table} }
      while ((m = reTable.exec(text))) { const table=m[2].replace(/`/g,''); const a=m[3].replace(/`/g,'').toLowerCase(); if (!alias[a]) alias[a] = { db: currentDb.value || '', table } }
      return alias
    }
    const dynamicSQLCompletion = (context: CompletionContext) => {
      // 使用 matchBefore 精准判断"以点结尾"的场景，稳定触发补全
      const amap = buildAliasMap(context.state)
      const dbs = buildDbList()

      // db.table.
      const dbTableDot = context.matchBefore(/[A-Za-z0-9_`]+\.[A-Za-z0-9_`]+\.$/)
      if (dbTableDot) {
        const txt = dbTableDot.text
        try { console.debug('[cm.complete] db.table. hit:', txt) } catch {}
        const [dbRaw, tableRaw] = txt.slice(0, -1).split('.')
        const db = dbRaw.replace(/`/g,'')
        const table = tableRaw.replace(/`/g,'')
        return fetchColumns(db, table).then(cols=>{
          try { console.debug('[cm.complete] db.table. columns:', cols) } catch {}
          // 光标位于最后一个点之后，from 取当前位置，避免把 "db.table." 也纳入过滤前缀
          return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ }
        }) as any
      }
      // alias. 或 表名.
      const aliasDot = context.matchBefore(/[A-Za-z0-9_`]+\.$/)
      if (aliasDot) {
        const token = aliasDot.text.replace('.', '').replace(/`/g,'')
        const hitAlias = amap[token.toLowerCase()]
        if (hitAlias) return fetchColumns(hitAlias.db||currentDb.value||'', hitAlias.table).then(cols=>{ try { console.debug('[cm.complete] alias columns:', cols) } catch {}; return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ } }) as any
        if (currentDb.value) {
          const known = tablesByKey[`${connId.value}::${currentDb.value}`] || []
          if (known.includes(token)) {
            return fetchColumns(currentDb.value, token).then(cols=>{ try { console.debug('[cm.complete] table columns:', cols) } catch {}; return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ } }) as any
          }
        }
        // 若是库. 则在下个分支处理
      }
      // db. → 表补全（即使本地列表未加载到该库名，也尝试请求）
      const dbDot = context.matchBefore(/[A-Za-z0-9_`]+\.$/)
      if (dbDot) {
        const dbName = dbDot.text.replace('.', '').replace(/`/g,'')
        try { console.debug('[cm.complete] db. hit:', dbName) } catch {}
        return fetchTables(dbName).then(list=>{ try { console.debug('[cm.complete] db. tables:', list) } catch {}; return { from: context.pos, options: (list||[]).map(t=>({label:t,type:'table'})), validFor:/[\w$]*$/ } }) as any
      }

      // 默认：通用词法 + 关键字/库/表列表
      const before = context.matchBefore(/[\w$\.\uFF0E\u3002]+$/)
      const word = (before?.text||'').trim()
      const items:any[] = []
      const parts = word.split('.')
      const pushAll = (arr:string[], type:string)=> arr.forEach(n=> items.push({label:n,type}))
      if (parts.length === 1) { items.push(...keywordList); pushAll(dbs, 'database'); if (currentDb.value) pushAll(tablesByKey[`${connId.value}::${currentDb.value}`]||[], 'table') }
      else if (parts.length === 2) {
        const [dbOrTable, maybeTable] = parts
        const dbHit = dbs.find(d=> String(d).toLowerCase()===dbOrTable.toLowerCase())
        if (dbHit && !maybeTable) return fetchTables(dbHit).then(list=>({ from: before ? before.from : context.pos, options: list.map(t=>({label:t,type:'table'})), validFor:/[\w$.]*$/ })) as any
        const hit = amap[dbOrTable.toLowerCase()]
        if (hit) return fetchColumns(hit.db||currentDb.value||'', hit.table).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
        if (currentDb.value) return fetchColumns(currentDb.value, dbOrTable).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
      } else if (parts.length >= 3) {
        const db = parts[0], table = parts[1]
        return fetchColumns(db, table).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
      }
      if (!items.length) items.push(...keywordList)
      try { console.debug('[cm.complete] default items:', items.slice(0,5)) } catch {}
      // 保持 CodeMirror 自身面板为主，不在此处弹自绘列表
      return { from: before ? before.from : context.pos, options: items, validFor:/[\w$\.\uFF0E\u3002]*$/ }
    }

    const state = EditorState.create({
      doc: '',
      extensions: [
        lineNumbers(),
        sql({ dialect: MySQL }),
        highlightActiveLine(),
        // 启用软折行，避免单行无限延伸
        EditorView.lineWrapping,
        syntaxHighlighting(defaultHighlightStyle),
        keymap.of([
          ...completionKeymap,
          { key: 'Ctrl-Space', run: startCompletion }
        ]),
        autocompletion({ override:[dynamicSQLCompletion], icons:false, defaultKeymap:true, activateOnTyping:true }),
        // 主题中开启折行
        EditorView.theme({
          '.cm-content': { whiteSpace: 'pre-wrap' }
        }),
        EditorView.updateListener.of((v:any)=>{
          if (v.docChanged) {
            try {
              const txt = v.state.doc.toString();
              (globalThis as any).__next_sql_text = txt;
              updateActiveTabText(txt)
            } catch {}
            // 在输入 '.' 后，主动触发一次补全（db. / t. / db.table.）
            try {
              const head = v.state.selection.main.head
              const prev = v.state.doc.sliceString(Math.max(0, head - 1), head)
              if (prev === '.') startCompletion(v.view)
            } catch {}
          }
          syncEditorScrollerOverflow()
        }),
        EditorView.theme({
          '&':{ height:'100%' },
          '.cm-scroller':{ overflow:'auto' },
          '.cm-gutters':{ borderRight:'1px solid #e5e7eb', background:'#f8fafc', color:'#94a3b8' },
          '.cm-gutterElement':{ padding:'0 8px', fontSize:'12px' },
          '.cm-content':{
            fontFamily:'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            fontSize:'13px',
            lineHeight:'1.6',
            whiteSpace:'pre'
          }
        })
      ]
    })
    cmView = new EditorView({
      state,
      parent: host,
      // 强制启用软折行（除样式外再从行为层兜底）
      extensions: []
    })
    // 初始标签
    if (!tabs.length) newTab()
    ensureActionBarVisible()
    try { cmView.focus() } catch {}
    // 监听容器尺寸变化，实时更新是否需要横向滚动
    try {
      if (editorResizeObserver) editorResizeObserver.disconnect()
      editorResizeObserver = new ResizeObserver(()=> syncEditorScrollerOverflow())
      if (editorWrapRef.value) editorResizeObserver.observe(editorWrapRef.value)
    } catch {}
    syncEditorScrollerOverflow()
  } catch {}
})

onUpdated(() => {
  setupToolbarObserver()
  ensureActionBarVisible()
  syncEditorScrollerOverflow()
})
</script>

<style scoped>
.sql-next { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
.hdr { display:flex; align-items:center; gap:10px; padding:10px 12px; background: linear-gradient(90deg,#e8f0fe,#dbe8ff); border-bottom:1px solid #c7d2fe; color:#0b57d0; }
.hdr .title{ font-weight:700; }
.hdr .brand{ width:22px; height:22px; object-fit:contain; }
.big-actions{ display:flex; gap:10px; margin-left:16px; }
.big-btn{ display:flex; flex-direction:column; align-items:center; justify-content:center; width:64px; height:56px; border:1px solid #c7d2fe; border-radius:10px; background:#fff; color:#0b57d0; cursor:pointer; }
.big-btn svg{ width:24px; height:24px; }
.big-btn span{ font-size:12px; margin-top:4px; }
.big-btn:hover{ background:#eef2ff; }
.layout { flex:1 1 auto; min-height:0; display:grid; grid-template-columns: var(--left-w,270px) 6px 1fr; overflow:hidden; width:100%; }
.left { background:#f8fafc; border-right:1px solid #e5e7eb; display:flex; flex-direction:column; min-width:0; overflow:hidden; }
.tree { flex:1 1 auto; min-height:0; overflow-y:auto !important; overflow-x:hidden; padding:6px; }
.left, .tree, .dbs, .tbls, .inst-hd, .db-hd { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: var(--dv-font-ui, 14px); }
.tree { scrollbar-width: thin; }
.tree::-webkit-scrollbar{ width: 10px; height: 10px; }
.tree::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px; }
.tree::-webkit-scrollbar-track{ background:transparent; }
.inst-hd,.db-hd { display:flex; align-items:center; gap:6px; padding:4px 6px; border-radius:6px; cursor:pointer; position:relative; }
.inst-hd:hover,.db-hd:hover{ background:#eef2ff; }
.arrow{ display:inline-block; width:10px; color:#64748b; }
.arrow.open{ transform:rotate(90deg); }
.ico{ width:14px; height:14px; color:#60a5fa; flex:0 0 auto; }
.ico.inst{ color:#34d399 }
.ico.db{ color:#60a5fa }
.ico.tbl{ color:#93c5fd; margin-right:4px }
.mini{ display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; color:#334155; position:absolute; right:6px; top:4px; }
.mini.filter.active{ background:#e6f0ff; border-color:#93c5fd; color:#0b57d0; }
/* 库级过滤输入：与库名同一行，显示在库名右侧，不覆盖库名 */
.db-filter-input{ position:static; margin-left:6px; height:22px; border:1px solid #cbd5e1; border-radius:4px; padding:0 6px; font-size:12px; min-width:140px; }
.dbs{ list-style:none; margin:0; padding:0 0 0 16px; }
.cats{ list-style:none; margin:0; padding:4px 0 0 16px; }
.tbls{ list-style:none; margin:0; padding:2px 0 0 16px; }
.tbl{ padding:2px 6px; border-radius:4px; cursor:pointer; position: relative; }
.tbl:hover{ background:#f1f5f9; }
.cat{ margin:2px 0; }
.cat-hd{ display:flex; align-items:center; gap:6px; padding:4px 6px; border-radius:4px; cursor:pointer; color:#0f172a; }
.cat-hd:hover{ background:#eef2ff; }
.table-hd{ display:flex; align-items:center; gap:6px; padding:2px 0; cursor:pointer; margin-left:2px; position: relative; padding-right:66px; min-height:24px; }
.table-hd .arrow{ display:inline-block; width:12px; transform: rotate(0deg); transition: transform .12s ease; }
.table-hd .arrow.open{ transform: rotate(90deg); }
.table-hd .inline-actions{ position:absolute; right:6px; top:50%; transform: translateY(-50%); display:flex; align-items:center; gap:8px; z-index:3; opacity:0; pointer-events:none; transition: opacity .12s ease; }
.tbl:hover .inline-actions, .table-hd:hover .inline-actions{ opacity:1; pointer-events:auto; }
.tb-act:hover{ background:#e6f0ff; border-color:#93c5fd; color:#0b57d0; }
.tb-act{ width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#0b57d0; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.tb-act svg{ width:14px; height:14px; display:block; }
.table-hd .inline-actions .mini:hover{ background:#e6f0ff; border-color:#93c5fd; }
.table-cats{ list-style:none; margin:4px 0 8px 28px; padding:0; background:transparent; border:0; }
.subcat{ display:flex; align-items:center; gap:8px; padding:4px 6px; margin:6px 0; color:#475569; cursor:default; border-radius:6px; }
.subcat:hover{ background:#f1f5f9; }
.columns{ list-style:none; margin:6px 0 8px 18px; padding:0; }
.col-name{ display:flex; align-items:center; gap:8px; padding:2px 0; color:#111827; font-size:14px; }
.col-name .name{ font-size:14px; }
.ico.pk{ width:14px; height:14px; color:#f59e0b; }
.ico.col2{ width:14px; height:14px; color:#60a5fa; }
.ico.idx2{ width:14px; height:14px; color:#60a5fa; }
.ico.cat-tables,.ico.cat-views,.ico.cat-func,.ico.cat-proc,.ico.cat-evt,.ico.col,.ico.idx,.ico.fk,.ico.trg,.ico.evt{ width:16px; height:16px; }
.muted{ color:#9ca3af; padding:6px; }
.panel{ position:absolute; top:0; z-index:1000; border:1px solid #e5e7eb; border-radius:8px; background:#fff; box-shadow:0 8px 16px rgba(0,0,0,.08); }
.inst-panel{ position: fixed; width: 320px; max-height: 360px; overflow:auto; }
.inst-panel .ph-search{ padding:6px 10px; border-bottom:1px solid #e5e7eb; background:#fff; position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; position: relative; }
.inst-panel .ph-search .ico{ position:absolute; left:18px; top:50%; transform:translateY(-50%); color:#94a3b8; font-size:14px; pointer-events:none; }
.inst-panel .ph-search input{ width:100%; height:26px; border:1px solid #c7d2fe; border-radius:6px; padding:2px 34px 2px 32px; font-size:13px; outline:none; }
.inst-panel .ph-search input:focus{ border-color:#c7d2fe; box-shadow:none; }
.inst-panel .ph-search .clear{ position:absolute; right:18px; top:50%; transform:translateY(-50%); width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; display:inline-flex; align-items:center; justify-content:center; }
.panel .phd{ display:flex; align-items:center; justify-content:space-between; padding:6px 8px; border-bottom:1px solid #e5e7eb; color:#0b57d0; font-weight:600; }
.panel .plist{ max-height:220px; overflow:auto; padding:6px 8px; }
.panel .opt{ display:block; padding:4px 6px; }
.gsearch{ border-top:1px solid #e5e7eb; padding:8px; flex:0 0 auto; }
.gsearch .searchbox{ position: relative; }
.gsearch .searchbox .ico{ position:absolute; left:8px; top:50%; transform:translateY(-50%); color:#94a3b8; font-size:14px; }
.gsearch .searchbox input{ width:100%; height:28px; padding:4px 64px 4px 28px; border:1px solid #c7d2fe; border-radius:6px; outline:none; }
.gsearch .searchbox input:focus{ border-color:#c7d2fe; box-shadow:none; }
.gsearch .searchbox .action{ position:absolute; top:50%; transform:translateY(-50%); right:8px; width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; cursor:pointer; margin-left:4px; }
.gsearch .searchbox .action + .action{ right:36px; }
.vsplit{ background:transparent; position:relative; cursor:col-resize; }
.vsplit::before{ content:""; position:absolute; left:2px; top:0; bottom:0; width:2px; background:#e5e7eb; }
.vsplit:hover::before{ background:#cbd5e1; }
.right{ position:relative; display:grid; grid-template-columns: 1fr 0; grid-template-rows: auto auto auto 8px 1fr; column-gap: 8px; min-height:0; min-width:0; z-index: 0; background:#f8fafc; height: calc(100vh - var(--statusbar-h)); }
.right.inspector-on{ grid-template-columns: 1fr var(--insp-w, 360px); }
.right > .editor-wrap{ margin-top:0; }
.toolbar{ display:none; }
.tabs{ margin:6px 12px 0 12px; min-width:0; overflow:hidden; position: sticky; top: 0; z-index: 10000; background: #f8fafc; border-bottom:1px solid #e5e7eb; min-height: 40px; }
.hdr-actions{ display:flex; gap:8px; align-items:center; margin-left:auto; }
.hdr-actions.sticky{ display:flex !important; visibility:visible !important; opacity:1 !important; pointer-events:auto !important; }
.hdr-actions .icon-btn{ width:32px; height:32px; border-radius:6px; border:1px solid #c9c9c9; background:#fff; color:#333; }
.hdr-actions .icon-btn.add{ background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.hdr-actions .icon-btn.warn{ background:#fff; border-color:#ef4444; color:#b91c1c; }
.hdr-actions .icon-btn.info{ background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.hdr-actions .icon-btn svg{ width:18px; height:18px; }
.tabs :deep(.tq-tabbar){ flex-wrap:nowrap; margin-bottom:0; height: 36px; align-items: flex-end; }
.hdr-actions{ display:flex; gap:8px; align-items:center; margin-left:auto; }
.hdr-actions.sticky{ display:flex !important; visibility:visible !important; opacity:1 !important; pointer-events:auto !important; }
.hdr-actions .icon-btn{ width:32px; height:32px; border-radius:6px; border:1px solid #d1d5db; background:#fff; color:#374151; box-shadow:none; transition: background-color .15s ease, box-shadow .15s ease, transform .06s ease; }
.hdr-actions .icon-btn.add{ background:#0b57d0; border-color:#0b57d0; color:#fff; }
.hdr-actions .icon-btn.warn{ background:#fff1f2; border-color:#fecaca; color:#b91c1c; }
.hdr-actions .icon-btn.info{ background:#e6f0ff; border-color:#c7d2fe; color:#0b57d0; }
.hdr-actions .icon-btn:hover{ background:#f5f7ff; box-shadow: 0 0 0 2px rgba(59,130,246,.25); }
/* 执行按钮在悬浮时保持蓝底并略微加深，不被通用 hover 覆盖 */
.hdr-actions .icon-btn.add:hover{ background:#0a49b7; border-color:#0a49b7; color:#fff; box-shadow: 0 0 0 2px rgba(59,130,246,.28); }
/* 停止与信息按钮的悬浮更明显一些 */
.hdr-actions .icon-btn.warn:hover{ background:#fecaca; box-shadow: 0 0 0 2px rgba(239,68,68,.25); }
.hdr-actions .icon-btn.info:hover{ background:#dbe8ff; box-shadow: 0 0 0 2px rgba(59,130,246,.22); }
.hdr-actions .icon-btn:active{ transform: translateY(1px); }
.hdr-actions .icon-btn:focus-visible{ outline: 2px solid #93c5fd; outline-offset: 2px; }
.hdr-actions .icon-btn svg{ width:16px; height:16px; }
.hdr-actions .icon-btn:disabled{ opacity:.6; cursor:not-allowed; box-shadow:none; }
.toolbar-actions .icon-btn{ width:32px; height:32px; border-radius:10px; }
.toolbar-actions .icon-btn svg{ width:18px; height:18px; }
.toolbar .tab, .tabs .tab{ display:flex; align-items:center; gap:6px; padding:6px 12px; background:#f7f9fc; border:1px solid #e5e7eb; border-bottom-color:#e5e7eb; border-radius:10px 10px 0 0; cursor:pointer; color:#374151; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: var(--dv-font-ui, 14px); box-shadow: 0 1px 2px rgba(0,0,0,.04); }
.toolbar .tab.active, .tabs .tab.active{ background:#fff; border-color:#99b7ff; border-bottom-color:#99b7ff; box-shadow: 0 0 0 2px rgba(59,130,246,.25); }
.toolbar .tab .close{ border:none; background:transparent; cursor:pointer; color:#64748b; }
.toolbar .add{ margin-left:6px; width:28px; height:28px; border:1px solid #e5e7eb; background:#fff; border-radius:8px; cursor:pointer; }
.editor-wrap{ position:relative; overflow: visible; flex: 0 0 auto; width:100%; z-index:1; min-height:0; }
.editor{ height:150px; min-height:0; overflow:hidden; position:relative; }
.tabs + .editor-wrap { margin-top: 0; }
.tab-toolbar { display:flex; align-items:center; gap:8px; padding:8px 12px; border-bottom:1px solid #e5e7eb; background:#f8fafc; }
.tab-toolbar .sel { height:28px; padding:0 8px; border:1px solid #c7d2fe; border-radius:6px; color:#0b57d0; }
.tab-toolbar .sp { flex:1 1 auto; }
.tab-toolbar .icon-btn{ width:28px; height:28px; border:1px solid #d1d5db; border-radius:6px; background:#fff; color:#374151; display:inline-flex; align-items:center; justify-content:center; }
.tab-toolbar .icon-btn.add{ background:#0b57d0; border-color:#0b57d0; color:#fff; }
.tab-toolbar .icon-btn.warn{ background:#fff1f2; border-color:#fecaca; color:#b91c1c; }
.tab-toolbar .icon-btn.info{ background:#e6f0ff; border-color:#c7d2fe; color:#0b57d0; }
.tab-toolbar .icon-btn svg{ width:16px; height:16px; }
.editor :deep(.cm-editor){ height:100% !important; max-width:100%; position: relative; z-index: 1; }
.editor :deep(.cm-scroller){ height:100%; overflow:auto; scrollbar-width: thin; padding-right:0; padding-bottom:0; max-width:100%; width: 100%; }
.editor :deep(.cm-content){
  white-space: pre-wrap !important; /* 自动折行 */
  word-break: break-word;
  min-width: 0 !important; /* 不撑开容器 */
}
.editor :deep(.cm-tooltip){ z-index: 30000; position: absolute; }
.editor :deep(.cm-tooltip-autocomplete){ z-index: 30010; }
.editor :deep(.cm-content) { caret-color: #111827; }
.editor :deep(.cm-cursor) { border-left-color: #111827 !important; }
.editor :deep(.cm-scroller::-webkit-scrollbar){ width:10px; height:10px; }
.editor :deep(.cm-scroller::-webkit-scrollbar-thumb){ background:#94a3b8; border-radius:6px; }
.editor :deep(.cm-scroller::-webkit-scrollbar-thumb:hover){ background:#64748b; }
.editor :deep(.cm-scroller::-webkit-scrollbar-track){ background:transparent; }
.hsplit{ height:24px; cursor:row-resize; position:relative; background:transparent; z-index:5; pointer-events:auto; }
.hsplit::before{ content:""; position:absolute; left:0; right:0; top:10px; height:3px; background:#cfd3dc; }
.fab-actions{ position:absolute; right:12px; top:6px; display:flex; gap:8px; z-index:30; pointer-events:auto; background:#f1f5f9; padding:4px 6px; border-radius:8px; box-shadow:0 6px 16px rgba(15,23,42,0.12); }
.code{ width:100%; height:100%; padding:10px; border:1px solid #e5e7eb; border-radius:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:13px; line-height:1.6; outline:none; overflow:auto; white-space: pre-wrap; }
.result{ display:flex; flex-direction:column; min-height:0; position:relative; z-index:1; background:#f8fafc; overflow:hidden; }
.rhdr{ padding:8px 12px; background:#f8fafc; border-bottom:1px solid #e5e7eb; }
.rbody{ flex:1 1 auto; min-height:0; overflow:auto; padding:12px; scrollbar-width: thin; scrollbar-color:#94a3b8 transparent; background:#f8fafc; position:relative; }
.rbody.table-mode{ padding:0; }
.rbody.table-mode .table-holder{ height:100%; display:flex; flex-direction:column; }
.rbody.table-mode :deep(.tq-table-fixed){ flex:1 1 auto; min-height:0; }
.rbody.table-mode :deep(.tq-scroll-x){ z-index: 2; }
.rbody.table-mode{ overflow: hidden; }
.rbody.table-mode :deep(.tq-body){ height:100%; overflow: auto; padding-bottom: var(--statusbar-h); box-sizing: border-box; }
.rbody::-webkit-scrollbar{ width:10px; height:10px }
.rbody::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px }
.rbody::-webkit-scrollbar-thumb:hover{ background:#64748b }
/* 结果表内部滚动容器：允许同时出现纵向/横向滚动条 */
.table-scroll{ overflow:auto; }
.x-scroll{ flex:0 0 auto; height:12px; min-height:12px; overflow-x:auto; overflow-y:hidden; border-top:1px solid #e5e7eb; background:#fff; }
.x-scroll{ display: var(--xscroll-visible, block); }
.x-scroll .spacer{ height:1px; }
/* 横向滚动条外观：与旧版一致（细拇指、圆角、浅灰） */
.x-scroll{ scrollbar-width: thin; scrollbar-color:#94a3b8 transparent; }
.x-scroll::-webkit-scrollbar{ height:10px; }
.x-scroll::-webkit-scrollbar-track{ background:transparent; }
.x-scroll::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px; }
.x-scroll:hover::-webkit-scrollbar-thumb{ background:#64748b; }
.tq-pagination{ flex:0 0 auto; display:flex; align-items:center; gap:12px; padding:8px 12px; border-top:1px solid #e5e7eb; background:#fff; color:#374151; }
.tq-pagination .muted{ color:#64748b; }
.tq-pagination .icon-btn{ width:28px; height:28px; border:1px solid #e5e7eb; border-radius:10px; background:#fff; color:#0b57d0; cursor:pointer; }
.tq-pagination .icon-btn:hover{ background:#f8fafc; }

.inspector{ border-left:1px solid #e5e7eb; background:#fff; display:flex; flex-direction:column; align-self:stretch; position: sticky; top: 0; height: 100%; max-height: 100%; overflow: auto; }
.insp-resizer{ cursor: col-resize; width: 6px; margin-left: -3px; background: transparent; position: sticky; top: 0; height: 100%; align-self:stretch; }
.insp-resizer:hover{ background: rgba(59,130,246,.2); }
.inspector-hd{ display:none; }
.inspector-hd .mini{ width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; }
.inspector-tabs{ display:flex; gap:8px; padding:6px 10px; border-bottom:1px solid #e5e7eb; position: sticky; top: 0; background:#fff; z-index:1; align-items:center; }
.inspector-tabs .sp{ flex:1 1 auto; }
.inspector-tabs .icon-btn{ width:28px; height:28px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; display:inline-flex; align-items:center; justify-content:center; }
.inspector-tabs .icon-btn.active{ background:#e6f0ff; border-color:#93c5fd; color:#0b57d0; }
.inspector-tabs .icon-btn.close{ border-color:#fecaca; color:#b91c1c; }
.inspector-body{ padding:10px; overflow:auto; }
.inspector-body .ddl{ white-space: pre; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 12px; line-height: 1.5; }
.cm-ddl :deep(.cm-editor){ height:auto; border:1px solid #e5e7eb; border-radius:6px; background:#fff; }
.cm-ddl :deep(.cm-scroller){ overflow:auto; }
.meta-item{ display:flex; gap:8px; padding:4px 0; font-size:13px; }
.meta-item .k{ color:#64748b; min-width:140px; }
.meta-item .v{ color:#0f172a; }
.tq-pagination input[type="number"]{ height:28px; line-height:28px; border:1px solid #e5e7eb; border-radius:8px; padding:2px 8px; box-sizing:border-box; color:#111827; }
.tq-pagination select{ height:28px; border:1px solid #e5e7eb; border-radius:8px; padding:2px 28px 2px 8px; color:#111827; }
/* 结果区占位提示：字体更小、更淡，便于与编辑区区分 */
.rbody .placeholder{ font-size: 13px; color:#9aa3b2; text-align:center; padding: 36px 8px; }
/* 浮动库过滤输入框样式 */
.db-filter-float{ position: fixed; z-index: 12000; height: 28px; padding: 4px 8px; border:1px solid #93c5fd; border-radius:6px; background:#fff; color:#0b57d0; box-shadow:0 8px 24px rgba(0,0,0,.15); width: 220px; outline:none; }
.db-filter-float:focus{ border-color:#93c5fd; box-shadow:0 0 0 2px rgba(147,197,253,.35); }
/* 移除自绘补全面板样式，使用 CodeMirror 自带面板 */
.no-select, .no-select *{ -webkit-user-select: none !important; user-select: none !important; }
/* 对象视图样式 */
.object-view{ display:flex; flex-direction:column; min-height:0; background:#fff; border-top:1px solid #e5e7eb; }
.object-view .ov-toolbar{ display:flex; align-items:center; gap:10px; padding:8px 12px; border-bottom:1px solid #e5e7eb; background:#f8fafc; }
.object-view .ov-toolbar .title{ font-weight:600; color:#0f172a; }
.object-view .ov-toolbar .sp{ flex:1 1 auto; }
.object-view .ov-toolbar .ov-search{ height:28px; border:1px solid #c7d2fe; border-radius:6px; padding:0 8px; }
.object-view .ov-body{ flex:1 1 auto; min-height:0; display:grid; grid-template-columns: 300px 1fr; }
.object-view .ov-list{ border-right:1px solid #e5e7eb; overflow:auto; }
.object-view .ov-item{ display:flex; align-items:center; padding:6px 10px; cursor:pointer; }
.object-view .ov-item:hover{ background:#eef2ff; }
.object-view .ov-item.active{ background:#e6f0ff; }
.object-view .ov-item .name{ white-space:nowrap; text-overflow:ellipsis; overflow:hidden; }
.object-view .ov-detail{ overflow:auto; display:flex; flex-direction:column; }
.object-view .ov-tabs{ display:flex; gap:6px; padding:6px 10px; border-bottom:1px solid #e5e7eb; position:sticky; top:0; background:#fff; }
.object-view .ov-tabs button{ height:28px; padding:0 10px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; cursor:pointer; }
.object-view .ov-tabs button.active{ background:#e6f0ff; border-color:#93c5fd; color:#0b57d0; }
.object-view .ov-panel{ padding:10px; overflow:auto; }
.object-view .ov-panel .ddl{ white-space: pre; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 12px; line-height: 1.5; }
.object-view .meta .row{ display:flex; gap:8px; padding:4px 0; font-size:13px; }
.object-view .meta .k{ color:#64748b; min-width:140px; }
.object-view .meta .v{ color:#0f172a; }
</style>


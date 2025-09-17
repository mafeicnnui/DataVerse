<template>
  <div class="tq-editor" :style="{ '--tq-editor-h': (ctx.tq.editorHeight || 120) + 'px', height: (ctx.tq.editorHeight || 120) + 'px' }" ref="tqEditorRefLocal">
    <!-- 独立容器，仅用于 SQL 控制台；由 ensureSqlEditor 接管为 contenteditable -->
    <div ref="tqCodeRefLocal" class="tq-sql-console" aria-label="SQL 编辑器" title="在此编写 SQL... 支持 Ctrl+Enter 执行"></div>
  </div>
  <div class="tq-resizer" title="拖动以调整编辑器与结果区域高度" @mousedown.prevent="ctx.startResize"></div>
  
</template>

<script setup lang="ts">
import { inject, ref, onMounted, watch, nextTick } from 'vue'
// 可控开关：仅当路由参数 cm=on 或环境变量 VITE_SQL_CONSOLE_CM=on 时启用 CodeMirror 高亮
import { EditorState } from '@codemirror/state'
import { EditorView, highlightActiveLine, keymap } from '@codemirror/view'
import { sql, MySQL } from '@codemirror/lang-sql'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'
import { autocompletion, CompletionContext, completionKeymap, startCompletion } from '@codemirror/autocomplete'
const ctx = inject<any>('tqCtx')
const tqEditorRefLocal = ref<HTMLElement | null>(null)
const tqCodeRefLocal = ref<HTMLElement | null>(null)
const cmView = ref<any | null>(null)

function getDbList(): string[] {
  try { return Array.isArray(ctx?.tq?.databases) ? ctx.tq.databases as string[] : [] } catch { return [] }
}
function getTablesMap(): Record<string, string[]> {
  try { return (ctx?.tq?.tables || {}) as Record<string, string[]> } catch { return {} }
}

onMounted(async () => {
  if (!ctx) return
  if (ctx.tqEditorRef) ctx.tqEditorRef.value = tqEditorRefLocal.value
  if (ctx.tqCodeRef) ctx.tqCodeRef.value = tqCodeRefLocal.value
  await nextTick()
  const host = tqCodeRefLocal.value as HTMLElement | null
  if (!host) return
  const sp = new URLSearchParams(location.search)
  const enableCM = sp.get('cm') === 'on' || (import.meta as any)?.env?.VITE_SQL_CONSOLE_CM === 'on'
  if (enableCM) {
    try {
      try { console.debug('[sql-console] cm=on detected') } catch {}
      // Shadow DOM 隔离挂载，避免外层被覆盖
      const domText = String(host.textContent || '')
      try { host.dataset.cmOn = '1' } catch {}
      host.innerHTML = ''
      host.removeAttribute('contenteditable')
      host.tabIndex = 0
      const shadow = (host.shadowRoot || host.attachShadow({ mode: 'open' })) as ShadowRoot
      // 清空 shadow 并注入样式与根节点
      try { while (shadow.firstChild) shadow.removeChild(shadow.firstChild) } catch {}
      const style = document.createElement('style')
      style.textContent = `:host{display:block;height:100%} .root{height:100%} .root *{box-sizing:border-box}`
      const root = document.createElement('div')
      root.className = 'root'
      shadow.append(style, root)
      const startDoc = (String(ctx?.tq?.sql || '').trim() || domText)
      // 补全：关键词 + 库/表/列（懒加载）
      const keywordList = [
        'SELECT','FROM','WHERE','GROUP BY','ORDER BY','LIMIT','OFFSET','JOIN','LEFT JOIN','RIGHT JOIN','INNER JOIN','OUTER JOIN','ON','AND','OR','NOT','IN','IS NULL','IS NOT NULL','LIKE','BETWEEN','INSERT','INTO','VALUES','UPDATE','SET','DELETE','CREATE','TABLE','VIEW','INDEX','DROP','ALTER','ADD','PRIMARY KEY'
      ].map(l => ({ label: l, type: 'keyword', apply: l }))

      // 简单缓存，避免重复请求与死循环
      const columnsCache = new Map<string, string[]>()
      const columnsPending = new Set<string>()
      const getColKey = (db: string, table: string) => `${db}.${table}`

      async function fetchColumns(db: string, table: string): Promise<string[]> {
        try {
          const key = getColKey(db, table)
          const cached = columnsCache.get(key)
          if (cached && cached.length) return cached
          if (columnsPending.has(key)) return []
          columnsPending.add(key)
          // 发送多组别名参数，兼容“工单查询中的接口”
          const cid = String(ctx?.tq?.selectedConnId || '')
          const params = new URLSearchParams({
            connId: cid,
            connectionId: cid,
            conn_id: cid,
            id: cid,
            db,
            database: db,
            schema: db,
            table,
            tableName: table,
            tbl: table,
            format: 'json',
          })
          // 首选 /api/ticket/columns（与截图一致），失败再回退 /ticket/columns
          const url1 = `/api/ticket/columns?${params.toString()}`
          const url2 = `/ticket/columns?${params.toString()}`
          let urlTried = url1
          try { console.debug('[cm] fetchColumns ->', url1) } catch {}
          let res = await fetch(url1, { headers: { 'Accept': 'application/json' } })
          if (!res.ok || !String(res.headers.get('content-type') || '').includes('application/json')) {
            try { console.warn('[cm] columns url1 not json/ok, try url2', url2) } catch {}
            urlTried = url2
            res = await fetch(url2, { headers: { 'Accept': 'application/json' } })
          }
          if (!res.ok) {
            columnsPending.delete(key)
            return []
          }
          const ctype = String(res.headers.get('content-type') || '')
          let data: any
          if (ctype.includes('application/json')) {
            data = await res.json()
          } else {
            // 有些后端返回 text/plain 但内容是 JSON，尝试解析文本
            try {
              const txt = await res.text()
              try { console.warn('[cm] columns non-json content-type:', ctype, 'len=', txt?.length) } catch {}
              if (txt && (txt.trim().startsWith('[') || txt.trim().startsWith('{'))) {
                data = JSON.parse(txt)
              }
            } catch {}
            // 尝试备用 REST 路径
            try {
              const alt = `/connections/${encodeURIComponent(String(ctx?.tq?.selectedConnId || ''))}/databases/${encodeURIComponent(db)}/tables/${encodeURIComponent(table)}/columns`
              console.warn('[cm] /ticket/columns not json, try alt:', alt)
              res = await fetch(alt, { headers: { 'Accept': 'application/json' } })
              if (res.ok && String(res.headers.get('content-type') || '').includes('application/json')) {
                data = await res.json()
              } else {
                columnsPending.delete(key)
                return []
              }
            } catch {
              columnsPending.delete(key)
              return []
            }
          }
          const norm = ((): string[] => {
            try {
              // 1) 直接数组
              if (Array.isArray(data)) {
                if (data.length && typeof data[0] === 'string') return data as string[]
                // 对象数组，尝试提取常见字段
                const keys = ['name','column','column_name','COLUMN_NAME','field','Field']
                return (data as any[]).map(o => {
                  for (const k of keys) if (o && typeof o[k] === 'string') return o[k]
                  return ''
                }).filter(Boolean)
              }
              // 2) 包裹在 data/columns 字段
              const arr = (data?.columns || data?.data)
              if (Array.isArray(arr)) {
                if (arr.length && typeof arr[0] === 'string') return arr as string[]
                const keys = ['name','column','column_name','COLUMN_NAME','field','Field']
                return (arr as any[]).map(o => {
                  for (const k of keys) if (o && typeof o[k] === 'string') return o[k]
                  return ''
                }).filter(Boolean)
              }
            } catch {}
            return []
          })()
          const uniq = Array.from(new Set(norm))
          try { console.debug('[cm] fetchColumns ok', { url: urlTried, rawCount: Array.isArray(data) ? data.length : (data?.columns||data?.data)?.length, normCount: uniq.length }) } catch {}
          columnsCache.set(key, uniq)
          columnsPending.delete(key)
          return uniq
        } catch {
          return []
        } finally {
          // 防止异常路径 pending 未清
          try { columnsPending.delete(`${db}.${table}`) } catch {}
        }
      }

      function findDbForTable(tablesMap: Record<string, string[]>, table: string): string | '' {
        try {
          for (const db of Object.keys(tablesMap || {})) {
            const arr = tablesMap[db]
            if (Array.isArray(arr) && arr.includes(table)) return db
          }
        } catch {}
        return ''
      }

      // 从当前文档中提取别名映射：alias -> { db, table }
      function buildAliasMap(state: EditorState): Record<string, { db: string, table: string }> {
        const text = state.doc.toString()
        const alias: Record<string, { db: string, table: string }> = {}
        // 常见书写：FROM db.table t / FROM db.table AS t / JOIN db.table t / JOIN db.table AS t
        const reDbTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s*\.\s*([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
        // 无库：FROM table t / JOIN table AS t
        const reTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
        let m: RegExpExecArray | null
        while ((m = reDbTable.exec(text))) {
          const db = m[2].replace(/`/g,'')
          const table = m[3].replace(/`/g,'')
          const a = m[4].replace(/`/g,'').toLowerCase()
          alias[a] = { db, table }
        }
        while ((m = reTable.exec(text))) {
          const table = m[2].replace(/`/g,'')
          const a = m[3].replace(/`/g,'').toLowerCase()
          // 若已有更明确的 db.table 别名，不覆盖
          if (!alias[a]) {
            const db = String(ctx?.tq?.selectedDb || '') || findDbForTable((ctx?.tq?.tables || {}) as any, table)
            alias[a] = { db, table }
          }
        }
        try { console.debug('[cm] alias map', alias) } catch {}
        return alias
      }

      async function fetchTables(db: string): Promise<string[]> {
        try {
          const params = new URLSearchParams({ connId: String(ctx?.tq?.selectedConnId || ''), db, database: db, schema: db })
          const res = await fetch(`/ticket/tables?${params.toString()}`)
          if (!res.ok) return []
          const data = await res.json()
          const list = Array.isArray(data) ? (data as string[]) : []
          try {
            if (ctx?.tq) {
              const map = (ctx.tq.tables || {}) as Record<string, string[]>
              map[db] = list
              ctx.tq.tables = map
            }
          } catch {}
          return list
        } catch { return [] }
      }

      const dynamicSQLCompletion = (context: CompletionContext) => {
        try { console.debug('[cm] completion enter', { pos: context.pos }) } catch {}
        // 支持 ASCII '.' 与全角点号 '．'(U+FF0E) 与中文句号 '。'(U+3002)
        let before = context.matchBefore(/[\w$\.\uFF0E\u3002]+$/)
        // 当光标正位于点号后（如 db. 或 db.table.）时，matchBefore 可能为空，这里主动触发
        if (!before) {
          const line = context.state.doc.lineAt(context.pos)
          const up = line.text.slice(0, context.pos - line.from)
          try { console.debug('[cm] completion no-before, up=', up) } catch {}
          // 情况一：db.
          let m = up.match(/([\w$]+)[\.\uFF0E\u3002]$/)
          if (m) {
            const dbOrTable = m[1]
            // 先看是否别名（alias.）
            const amap = buildAliasMap(context.state)
            const hitAlias = amap[dbOrTable.toLowerCase()]
            if (hitAlias) {
              const pendKey = getColKey(hitAlias.db || '', hitAlias.table)
              if (columnsPending.has(pendKey) && !context.explicit) return null
              return fetchColumns(hitAlias.db || '', hitAlias.table).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
            }
            // db. -> 列出该库的表
            let dbs: string[] = Array.isArray(ctx?.tq?.databases) ? ctx.tq.databases : []
            if (!dbs.length) {
              try { dbs = Object.keys((ctx?.tq?.tables || {}) as Record<string,string[]>) } catch {}
            }
            const dbHit = dbs.find(d => String(d).toLowerCase() === dbOrTable.toLowerCase())
            try { console.debug('[cm] dot-db match', { input: dbOrTable, dbs, dbHit }) } catch {}
            if (dbHit) {
              const cached = (ctx?.tq?.tables || {})[dbHit] as string[] | undefined
              if (Array.isArray(cached) && cached.length) {
                try { console.debug('[cm] use cached tables', { db: dbHit, count: cached.length }) } catch {}
                return { from: context.pos, options: cached.map(t => ({ label: t, type: 'table' })), validFor: /[\w$.]*$/ }
              }
              return fetchTables(dbHit).then(list => {
                try { console.debug('[cm] fetched tables', { db: dbHit, count: list.length }) } catch {}
                // 再次主动打开补全，确保结果显示
                try { startCompletion((context as any).view) } catch {}
                return { from: context.pos, options: list.map(t => ({ label: t, type: 'table' })), validFor: /[\w$.]*$/ }
              }) as any
            }
            // table.（当前库或根据缓存推断）-> 列出列
            let curDb = String(ctx?.tq?.selectedDb || '')
            if (!curDb) {
              const map = (ctx?.tq?.tables || {}) as Record<string, string[]>
              curDb = findDbForTable(map, dbOrTable)
            }
            // alias. -> 列出列（基于 FROM/JOIN 的别名）
            if (!curDb) {
              const amap = buildAliasMap(context.state)
              const hit = amap[dbOrTable.toLowerCase()]
              if (hit) {
                const pendKey = getColKey(hit.db || curDb || '', hit.table)
                if (columnsPending.has(pendKey) && !context.explicit) return null
                return fetchColumns(hit.db || curDb || '', hit.table).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
              }
            }
            if (curDb) {
              try { console.debug('[cm] columns via table. with currentDb', curDb, dbOrTable) } catch {}
              const pendKey = getColKey(curDb, dbOrTable)
              if (columnsPending.has(pendKey) && !context.explicit) return null
              return fetchColumns(curDb, dbOrTable).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
            }
          }
          // 情况二：db.table.
          m = up.match(/([\w$]+)[\.\uFF0E\u3002]([\w$]+)[\.\uFF0E\u3002]$/)
          if (m) {
            const db = m[1]
            const table = m[2]
            try { console.debug('[cm] dot-db.table predict columns', { db, table }) } catch {}
            const pendKey = getColKey(db, table)
            if (columnsPending.has(pendKey) && !context.explicit) return null
            return fetchColumns(db, table).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
          }
          if (!context.explicit) return null
        }
        const word = (before?.text || '').trim()
        try { console.debug('[cm] completion before=', before?.text) } catch {}
        const dbs: string[] = Array.isArray(ctx?.tq?.databases) ? ctx.tq.databases : []
        const tablesMap: Record<string, string[]> = (ctx?.tq?.tables || {}) as any
        const items: any[] = []

        // 解析形态： db.table.col 或 db.table 或 table.col
        const parts = word.split('.')
        try { console.debug('[cm] completion parts=', parts) } catch {}
        const pushAll = (arr: string[], type: string) => arr.forEach(n => items.push({ label: n, type }))

        const prevCh = context.state.doc.sliceString(Math.max(0, context.pos - 1), context.pos)
        if (parts.length === 1) {
          // 关键词 + 库名 + 可能的当前库表名
          items.push(...keywordList)
          pushAll(dbs, 'database')
          const curDb = String(ctx?.tq?.selectedDb || '')
          if (curDb && Array.isArray(tablesMap[curDb])) pushAll(tablesMap[curDb], 'table')
        } else if (parts.length === 2) {
          const [dbOrTable, maybeTable] = parts
          const dbHit = dbs.find(d => String(d).toLowerCase() === dbOrTable.toLowerCase())
          // 若刚刚输入的是点号：
          // - 当第二段为空（例如 "db."），应该列出“表名”，而不是请求列
          // - 仅当第二段非空（例如 "db.table" 后再输入 .）才进入“列补全”
          if (prevCh === '.') {
            const hasTable = !!String(maybeTable || '').trim()
            if (dbHit && !hasTable) {
              // db. -> 表名
              const cached = tablesMap[dbHit]
              if (Array.isArray(cached) && cached.length) {
                pushAll(cached, 'table')
                return { from: context.pos, options: items, validFor: /[\w$.]*$/ } as any
              }
              return fetchTables(dbHit).then(list => ({
                from: context.pos,
                options: list.map(t => ({ label: t, type: 'table' })),
                validFor: /[\w$.]*$/
              })) as any
            }
            // alias.（无第二段）优先尝试别名 -> 列
            if (!hasTable) {
              const amap0 = buildAliasMap(context.state)
              const hit0 = amap0[dbOrTable.toLowerCase()]
              if (hit0) {
                const pendKey = getColKey(hit0.db || '', hit0.table)
                if (columnsPending.has(pendKey) && !context.explicit) return null
                return fetchColumns(hit0.db || '', hit0.table).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
              }
              // 没有别名命中，避免把别名当表名误请求
              return null
            }
            if (hasTable) {
              // 支持别名: alias. 列补全（FROM/JOIN … AS alias）
              const amap = buildAliasMap(context.state)
              const hit = amap[dbOrTable.toLowerCase()]
              if (hit) {
                const pendKey = getColKey(hit.db || '', hit.table)
                if (columnsPending.has(pendKey) && !context.explicit) return null
                return fetchColumns(hit.db || '', hit.table).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
              }
              if (dbHit) {
                try { console.debug('[cm] columns via db.table.', dbHit, maybeTable) } catch {}
                const pendKey = getColKey(dbHit, String(maybeTable))
                if (columnsPending.has(pendKey) && !context.explicit) return null
                return fetchColumns(dbHit, String(maybeTable)).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
                const curDb = String(ctx?.tq?.selectedDb || '')
                if (curDb) {
                  try { console.debug('[cm] columns via table. with currentDb', curDb, dbOrTable) } catch {}
                  const pendKey = getColKey(curDb, dbOrTable)
                  if (columnsPending.has(pendKey) && !context.explicit) return null
                  return fetchColumns(curDb, dbOrTable).then(cols => ({ from: context.pos, options: cols.map(c => ({ label: c, type: 'property' })), validFor: /[\w$.]*$/ })) as any
                }
              }
            }
          }
          if (dbHit) {
            // db.table 层级：若本地无缓存则懒加载
            const cached = tablesMap[dbHit]
            if (Array.isArray(cached) && cached.length) {
              pushAll(cached, 'table')
              return { from: context.pos, options: items, validFor: /[\w$.]*$/ } as any
            } else {
              const pendKey = getColKey(dbHit, String(maybeTable || ''))
              if (columnsPending.has(pendKey) && !context.explicit) return null
              return fetchTables(dbHit).then(list => ({
                from: context.pos,
                options: list.map(t => ({ label: t, type: 'table' })),
                validFor: /[\w$.]*$/
              })) as any
            }
          } else {
            // table.col（当前库）
            const curDb = String(ctx?.tq?.selectedDb || '')
            if (curDb) {
              const pendKey = getColKey(curDb, dbOrTable)
              if (columnsPending.has(pendKey) && !context.explicit) return null
              return fetchColumns(curDb, dbOrTable).then(cols => ({
                from: context.pos,
                options: cols.map(c => ({ label: c, type: 'property' })),
                validFor: /[\w$.]*$/
              })) as any
            }
          }
        } else if (parts.length >= 3) {
          // db.table.col -> 提示列
          const db = parts[0], table = parts[1]
          const pendKey = getColKey(db, table)
          if (columnsPending.has(pendKey) && !context.explicit) return null
          return fetchColumns(db, table).then(cols => ({
            from: context.pos,
            options: cols.map(c => ({ label: c, type: 'property' })),
            validFor: /[\w$.]*$/
          })) as any
        }

        if (!items.length) {
          // 兜底给出关键词，保证面板可以出现
          items.push(...keywordList)
        }
        return { from: before ? before.from : context.pos, options: items, validFor: /[\w$\.\uFF0E\u3002]*$/ }
      }

      // dot 触发节流，避免连续重触发导致日志刷屏/反复打开面板
      let lastDotTs = 0
      let lastDotPos = -1

      const state = EditorState.create({
        doc: startDoc,
        extensions: [
          sql({ dialect: MySQL }),
          highlightActiveLine(),
          syntaxHighlighting(defaultHighlightStyle),
          keymap.of(completionKeymap),
          autocompletion({ override: [dynamicSQLCompletion], icons: false, defaultKeymap: true, activateOnTyping: true }),
          EditorView.updateListener.of((v: any) => {
            if (v.docChanged) {
              try {
                const txt = v.state.doc.toString()
                ctx.tq.sql = txt
                // 同步到全局，供组合式 executeSQL 读取
                ;(globalThis as any).__tq_sql_text = txt
              } catch {}
              try {
                const head = v.state.selection.main.head
                const prev = v.state.doc.sliceString(Math.max(0, head - 1), head)
                if (prev === '.') {
                  const now = Date.now()
                  if (now - lastDotTs > 300 || head !== lastDotPos) {
                    console.debug('[cm] updateListener dot detected')
                    startCompletion(v.view)
                    lastDotTs = now
                    lastDotPos = head
                  }
                }
              } catch {}
            }
          }),
          EditorView.inputHandler.of((view: any, from: number, to: number, text: string) => {
            try {
              if (text === '.') {
                const now = Date.now()
                if (now - lastDotTs > 300 || (from + 1) !== lastDotPos) {
                  console.debug('[cm] inputHandler dot typed')
                  setTimeout(() => { try { startCompletion(view) } catch {} }, 0)
                  lastDotTs = now
                  lastDotPos = from + 1
                }
              }
            } catch {}
            return false // 不拦截输入
          }),
          EditorView.theme({
            '&': { height: '100%' },
            '.cm-scroller': { overflow: 'auto' },
            '.cm-content': { fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace', fontSize: '13px', lineHeight: '1.6' },
          }),
        ]
      })
      const view = new EditorView({ state, parent: root })
      cmView.value = view
      try { (host as any)._dvBound = true; host.dataset.cm = '1' } catch {}
      try {
        (view as any).focus(); host.focus()
        // 初始同步一次到全局，供 executeSQL 读取
        try { (globalThis as any).__tq_sql_text = view.state.doc.toString() } catch {}
      } catch {}
      try {
        const cur = view.state.doc.toString()
        const seed = (String(ctx?.tq?.sql || '').trim() || domText)
        if (!cur && seed) {
          view.dispatch({ changes: { from: 0, to: 0, insert: seed } })
          try { console.debug('[sql-console] seeded from dom/ctx, len=', seed.length) } catch {}
        }
      } catch {}
      try { console.debug('[sql-console] CM mounted (shadow)') } catch {}
      // 若 shadow 内仍未出现 .cm-editor，则回退
      setTimeout(() => {
        try {
          if (!shadow.querySelector('.cm-editor')) {
            console.warn('[sql-console] CM not visible in shadow -> fallback')
            ;(host as any)._dvBound = false
            ensureFallback(host)
          }
        } catch {}
      }, 0)
      return
    } catch (e) {
      try { console.warn('[sql-console] CM failed:', e) } catch {}
      // 失败则回退
    }
  }
  ensureFallback(host)
})

// 高度变化后触发一次重排，帮助编辑器根据新高度刷新布局
watch(() => ctx?.tq?.editorHeight, async () => {
  await nextTick()
  try { await (ctx as any)?.ensureSqlEditor?.(tqCodeRefLocal.value as any) } catch {}
  try {
    // 通知浏览器做一次重排，兼容性最好
    window.dispatchEvent(new Event('resize'))
  } catch {}
  try {
    const el = tqEditorRefLocal.value as HTMLElement | null
    if (el && ctx?.tq?.editorHeight) {
      el.style.height = `${ctx.tq.editorHeight}px`
    }
  } catch {}
})

function ensureFallback(host: HTMLElement | null) {
  try { if (host) { delete (host as any)._dvBound; host.removeAttribute('data-cm'); host.removeAttribute('data-cm-on'); host.removeAttribute('data-cmOn') } } catch {}
  try { (ctx as any)?.ensureSqlEditor?.(host as any) } catch {}
  try { cmView.value = null } catch {}
}

// 外部修改 sql 时，同步到编辑器
watch(() => ctx?.tq?.sql, (val) => {
  try {
    const v = cmView.value
    if (!v) return
    const cur = v.state.doc.toString()
    const next = String(val ?? '')
    if (cur !== next) {
      v.dispatch({ changes: { from: 0, to: cur.length, insert: next } })
    }
  } catch {}
})
</script>

<style scoped>
/* 下沉自 App.vue 的编辑器容器样式，确保在子组件内生效 */
/* 容器宽度拉满且不以 flex-basis 影响宽度（避免在父级 row-flex 下变成宽度=高度） */
/* 让 SQL 容器与 CodeMirror 占满高度（避免父组件 scoped 样式失效） */
.tq-editor { height: var(--tq-editor-h, 120px); min-height: 120px; box-sizing: border-box; }
/* SQL 控制台专用容器（fallback 模式下确保换行与可选中） */
.tq-sql-console { width: 100%; height: 100%; box-sizing: border-box; padding: 8px; outline: none; border: none; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; user-select: text; }
/* 当启用 cm=on 时，确保 CodeMirror 可见且可聚焦 */
.tq-editor :deep(.cm-editor) { width: 100%; height: 100% !important; min-height: 0; box-sizing: border-box; padding: 10px; border: 1px solid #e5e7eb; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 13px; line-height: 1.6; }
.tq-editor :deep(.cm-editor .cm-scroller) { height: 100% !important; overflow: auto !important; }
.tq-editor :deep(.cm-editor .cm-content) { min-height: 100% !important; white-space: pre-wrap; }
/* 控制台统一使用 App.vue 的 .tq-vsplit 作为唯一分割条，这里隐藏组件内的 .tq-resizer */
.tq-resizer { display: none !important; }
.tq-resizer::before, .tq-resizer::after { display: none !important; content: none !important; }
</style>

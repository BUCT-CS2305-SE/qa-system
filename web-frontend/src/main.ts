import './styles/app.css';

// 说明：本文件仅用于“像 FastGPT 发布聊天页一样”的静态 UI 占位。
// - 不请求接口
// - 不实现发送/点击等交互（后续接入后端时再补）

function mountApp() {
  const root = document.getElementById('app');
  if (!root) throw new Error('#app not found');

  root.innerHTML = `
  <div class="fgLayout">
    <aside class="fgSidebar">
      <div class="fgBrand">
        <div class="fgBrandLogo" aria-hidden="true"></div>
        <div class="fgBrandText">
          <div class="fgBrandTitle">中国图书馆 QA</div>
          <div class="fgBrandSub">离线 UI 占位（仿 FastGPT 发布页结构）</div>
        </div>
      </div>

      <div class="fgSideSection">
        <div class="fgSideSectionTitle">会话</div>
        <div class="fgChatList">
          <div class="fgChatListItem active">
            <div class="fgChatListItemTitle">默认会话</div>
            <div class="fgChatListItemSub">最近：关于《红楼梦》的提问</div>
          </div>
          <div class="fgChatListItem">
            <div class="fgChatListItemTitle">历史会话（占位）</div>
            <div class="fgChatListItemSub">最近：关于敦煌资料的查询</div>
          </div>
        </div>
      </div>

      <div class="fgSideSection">
        <div class="fgSideSectionTitle">提示</div>
        <div class="fgSideHint">
          这是一个静态页面：
          <ul>
            <li>包含侧边栏、头像、气泡、输入框</li>
            <li>不实现按钮点击与接口调用</li>
            <li>后续对接 Spring：<code>/api/qa/ask</code></li>
          </ul>
        </div>
      </div>

      <div class="fgSideFooter">
        <div class="fgSideFooterItem">
          <span class="dot online"></span>
          <span>UI 状态：静态占位</span>
        </div>
      </div>
    </aside>

    <main class="fgMain">
      <header class="fgTopbar">
        <div class="fgTopbarLeft">
          <div class="fgTopbarTitle">问答</div>
          <div class="fgTopbarDesc">中国图书馆知识问答（Demo UI）</div>
        </div>
        <div class="fgTopbarRight">
          <div class="fgBadge">Neo4j</div>
          <div class="fgBadge">pgvector</div>
          <div class="fgBadge">Mongo</div>
          <div class="fgBadge">Redis</div>
        </div>
      </header>

      <section class="fgChat">
        <div class="fgMsgRow">
          <div class="fgAvatar bot" aria-hidden="true"></div>
          <div class="fgBubble">
            <div class="fgBubbleText">你好，我是中国图书馆 QA 助手。你可以问我：馆藏图书、主题资料、作者信息、文本出处等。</div>
            <div class="fgBubbleMeta">助手 · 09:30</div>
          </div>
        </div>

        <div class="fgMsgRow user">
          <div class="fgBubble user">
            <div class="fgBubbleText">这本书《红楼梦》的作者是谁？</div>
            <div class="fgBubbleMeta">你 · 09:31</div>
          </div>
          <div class="fgAvatar user" aria-hidden="true"></div>
        </div>

        <div class="fgMsgRow">
          <div class="fgAvatar bot" aria-hidden="true"></div>
          <div class="fgBubble">
            <div class="fgBubbleText">
              《红楼梦》一般认为作者为曹雪芹，现存版本多为程伟元、高鹗整理刊行（示例回答，仅用于页面占位）。
            </div>

            <div class="fgQuoteTitle">来源</div>
            <div class="fgQuoteList">
              <div class="fgQuoteItem">
                <div class="fgQuoteTag">neo4j</div>
                <div class="fgQuoteBody">
                  <div class="fgQuoteName">图谱：书目节点 /Book{title: 红楼梦}</div>
                  <div class="fgQuoteDesc">证据：author = 曹雪芹（示例）</div>
                  <div class="fgQuoteLink">https://example.org/neo4j/source/book</div>
                </div>
              </div>
              <div class="fgQuoteItem">
                <div class="fgQuoteTag">doc</div>
                <div class="fgQuoteBody">
                  <div class="fgQuoteName">文档：馆藏导读（chunk #12）</div>
                  <div class="fgQuoteDesc">证据：……曹雪芹著，后由程高整理刊刻……（示例）</div>
                  <div class="fgQuoteLink">https://example.org/docs/source/chunk/12</div>
                </div>
              </div>
            </div>

            <div class="fgBubbleMeta">助手 · 09:31</div>
          </div>
        </div>
      </section>

      <footer class="fgComposer">
        <div class="fgComposerInner">
          <div class="fgInputWrap">
            <div class="fgInputIcon" aria-hidden="true"></div>
            <textarea class="fgInput" placeholder="输入问题（当前为静态占位，不发送）" rows="1"></textarea>
          </div>
          <button class="fgSendBtn" type="button" disabled>发送</button>
        </div>
        <div class="fgComposerHint">提示：后续接入后端时，替换为调用 Spring 的 <code>/api/qa/ask</code> 即可。</div>
      </footer>
    </main>
  </div>
  `;
}

mountApp();

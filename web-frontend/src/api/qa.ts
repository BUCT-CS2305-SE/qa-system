export type Source = { source_name: string; detail_url?: string };
export type QAResponse = {
  request_id?: string;
  answer: string;
  no_data?: boolean;
  sources?: Source[];
  facts?: Array<{ key: string; value: string; evidence?: string }>;
};

// mock ask implementation — 可替换为真实 fetch
export async function ask(question: string): Promise<QAResponse> {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (!question || /无|没有|不知道/.test(question)) {
        resolve({ answer: '暂无相关数据', no_data: true, sources: [] });
        return;
      }
      if (/博物馆|收藏/.test(question)) {
        resolve({
          answer: '此文物现藏于示例博物馆。',
          sources: [{ source_name: '示例博物馆', detail_url: 'https://example.org/museum/1' }],
          facts: [{ key: 'location', value: '示例博物馆', evidence: 'KG:artifact.location' }]
        });
        return;
      }

      resolve({
        answer: '这是一个演示回答（mock），后端接口未接入或返回占位内容。',
        sources: [{ source_name: '示例来源', detail_url: 'https://example.org/source/1' }],
        facts: []
      });
    }, 600);
  });
}

export async function getHistory() {
  return Promise.resolve([
    { id: 'h1', title: '默认会话', last: '关于青铜器铭文的提问' },
    { id: 'h2', title: '敦煌研究', last: '敦煌资料的年代判断' }
  ]);
}

export async function getSource(id: string) {
  return Promise.resolve({
    id,
    name: '示例来源',
    url: 'https://example.org/source/' + id,
    excerpt: '这是示例摘录'
  });
}

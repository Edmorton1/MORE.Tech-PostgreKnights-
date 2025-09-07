export const setModalContent = (modal, analyze) => {
  const showIssues = (issues) =>
    issues.map(
      (issue) =>
        `<div>
        <div>Тяжесть: ${issue.severity}</div>
        <div>Проблема: ${issue.problem}</div>
        <div>Рекомендация ${issue.recommendation}</div>
      </div>`
    );

  const content = `<div>
      <div>Анализ запроса ${analyze.post_analyze.query}</div>
      <div>Время: ${analyze.post_analyze.time}</div>
      <div>Стоимость: ${analyze.post_analyze.total_cost}</div>
      <div>Объём сканируемых данных: ${analyze.post_analyze.volume}</div>
      <div>Пре-анализ запроса</div>
			${showIssues(analyze.pre_analyze)}
			<div>Пост-анализ запроса: </div>
      ${showIssues(analyze.post_analyze.issues)}
    </div>`;

  modal.innerHTML = content;
};

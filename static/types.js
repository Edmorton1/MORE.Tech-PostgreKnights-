/**
 * @typedef {Object} AnalyzeIssue
 * @property {'low'|'medium'|'high'} severity
 * @property {string} problem
 * @property {string} recommendation
 */

/**
 * @typedef {Record<string, number>} Volume
 */

/**
 * @typedef {Object} PostAnalyze
 * @property {string} query
 * @property {string | number} time
 * @property {Volume} volume
 * @property {number} total_cost
 * @property {AnalyzeIssue[]} issues
 */

/**
 * @typedef {Object} StatisticItem
 * @property {string} query_single_line
 * @property {number} calls
 * @property {number} total_exec_time
 * @property {number} mean_exec_time
 * @property {number} rows
 */

/**
 * @typedef {Object} AnalyzeResult
 * @property {AnalyzeIssue[]} pre_analyze
 * @property {PostAnalyze} post_analyze
 * @property {StatisticItem[]} statistic
 */

/** @type {AnalyzeResult} */

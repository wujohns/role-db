/**
 * pm2 启动配置
 *
 * @author nobody
 * @date 23/02/28
 */
const path = require('path')

module.exports = {
  apps: [
    {
      name: 'role-service',
      script: 'hypercorn.sh',
      cwd: `${ __dirname }/role-service`,    // 执行命令前会提前切到的路径

      out_file: path.join(__dirname, './logs/out.log'),   // 普通日志路径
      error_file: path.join(__dirname, './logs/err.log'), // 错误日志路径
      pid_file: path.join(__dirname, './run/server.pid'), // 进程文件
      merge_logs: true,
      log_data_format: 'MM-DD HH:mm:ss',

      max_memory_restart: '400M',   // 超出该内存则进行重启
      kill_timeout: 5000,    // pm2 kill 时的最长时间
      exec_mode: 'fork'      // node工程优先使用 cluster 模式
    }
  ]
}
main 里面有两个配置文件，分别是
platform.yaml 
process.yaml

平台设置的一些配置，比如平台本身的配置
部分用来吃 process 相关的基础配置，比如库的配置

各个flow 里面也有两个配置
dependency.yaml 用来配置该flow 所有子step之间的关系
config.yaml 用来配置该flow 所有需要的default 设置
利用 edp_configkit 库，我们很容易拿到一个最终的merge 配置
最终user的配置等于
platform.yaml + process.yaml + config.yaml + dependency.yaml + user_config.yaml（user本地）


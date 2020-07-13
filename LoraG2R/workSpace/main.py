
# coding: utf-8
#开机自动运行main.py，无重要内容
import gc
gc.collect()    #回收内存

import sx127x
gc.collect()

import test
# import test_dual_channels as test
gc.collect()
test.main()     #指向测试主函数



# https://buymeacoffee.com/apintio


import wowint
import re
import struct
import random
import socket
import threading
import websockets
import asyncio
import time
import ntplib

import socket
import struct

import time

from iid42 import SendUdpIID



class WowIntegerTarget:
    """
    Manual: https://github.com/EloiStree/2024_08_29_ScratchToWarcraft
    """
        
    def __init__(self, ipv4:str = "127.0.0.1", port:int=7073, target_player_index:int=0, use_ntp:bool = True):
        self.ivp4 = ipv4
        self.port = port
        self.index = target_player_index
        self.target = SendUdpIID(ipv4, port, use_ntp)
        
    def press_key_int(self, press_key:int, delay_in_millisecond:int = 0.0):
        self.target.push_bytes(wowint.iid_ms(self.index,press_key,delay_in_millisecond))
    
    def release_key_int(self, press_key:int, delay_in_millisecond:int = 0.0):
        self.target.push_bytes(wowint.iid_ms(self.index,press_key+1000,delay_in_millisecond))
    
    def press_then_release_key_int(self, press_key:int, delay_in_milliseconds:int = 0, press_duration_milliseconds:int = 0):
        self.press_key_int(press_key,delay_in_milliseconds)
        self.release_key_int(press_key+1000,delay_in_milliseconds+press_duration_milliseconds)
        
        
        
        
        

"""
Reference of the integer of the keyboard.
It allows to give a request of what to do on the remote computer.
The enum is based on window keyboard.
"""   
class WowIntegerKeyboard:
        
    
        jump:int = 1032
        numpad_0:int = 1096
        numpad_1:int = 1097
        numpad_2:int = 1098
        numpad_3:int = 1099
        numpad_4:int = 1100
        numpad_5:int = 1101
        numpad_6:int = 1102
        numpad_7:int = 1103
        numpad_8:int = 1104
        numpad_9:int = 1105
        numpad_multiply:int = 1106
        numpad_add:int = 1107
        numpad_separator:int = 1108
        numpad_subtract:int = 1109
        numpad_decimal:int = 1110
        numpad_divide:int = 1111
        f1:int = 1112
        f2:int = 1113
        f3:int = 1114
        f4:int = 1115
        f5:int = 1116
        f6:int = 1117
        f7:int = 1118
        f8:int = 1119
        f9:int = 1120
        f10:int = 1121
        f11:int = 1122
        f12:int = 1123
        arrow_left:int = 1037    
        arrow_up:int = 1038
        arrow_right:int = 1039 
        arrow_down:int = 1040
        alpha_0:int = 1048
        alpha_1:int = 1049
        alpha_2:int = 1050
        alpha_3:int = 1051
        alpha_4:int = 1052
        alpha_5:int = 1053
        alpha_6:int = 1054
        alpha_7:int = 1055
        alpha_8:int = 1056
        alpha_9:int = 1057
        key_a:int = 1065
        key_b:int = 1066
        key_c:int = 1067
        key_d:int = 1068
        key_e:int = 1069
        key_f:int = 1070
        key_g:int = 1071
        key_h:int = 1072
        key_i:int = 1073
        key_j:int = 1074
        key_k:int = 1075
        key_l:int = 1076
        key_m:int = 1077
        key_n:int = 1078
        key_o:int = 1079
        key_p:int = 1080
        key_q:int = 1081
        key_r:int = 1082
        key_s:int = 1083
        key_t:int = 1084
        key_u:int = 1085
        key_v:int = 1086
        key_w:int = 1087
        key_x:int = 1088
        key_y:int = 1089
        key_z:int = 1090
        left_windows:int = 1091
        right_windows:int = 1092
        applications:int = 1093
        backspace:int = 1008
        tab:int = 1009
        clear:int = 1012
        enter:int = 1013
        shift:int = 1016
        control:int = 1017
        alt:int = 1018
        pause:int = 1019
        caps_lock:int = 1020
        escape:int = 1027
        space:int = 1032
        page_up:int = 1033
        page_down:int = 1034
        end:int = 1035
        home:int = 1036
        print_screen:int = 1044
        print:int= 1042
        scroll_lock:int = 1144
        num_lock:int = 1144
        insert:int = 1045
        delete:int = 1046
        left_shift:int = 1160
        right_shift:int = 1161
        left_control:int = 1162
        right_control:int = 1163
        left_alt:int = 1164
        right_alt:int = 1165
        volume_mute:int = 1173
        volume_down:int = 1174
        volume_up:int = 1175
        media_next:int = 1176
        media_previous:int = 1177
        media_stop:int = 1178
        media_play:int = 1179
        oem_1:int = 1186
        oem_plus:int = 1187
        oem_comma:int = 1188
        oem_minus:int = 1189
        oem_period:int = 1190
        oem_2:int = 1191
        oem_3:int = 1192
        oem_4:int = 1219
        oem_5:int = 1220
        oem_6:int = 1221
        oem_7:int = 1222
        oem_8:int = 1223
        oem_102:int = 1226
        play:int = 1250
        zoom:int = 1251
        
        
        
        

"""
Represent mapping to remote control a xbox gamepad with event.
"""
class XboxIntegerAction:
            random_input =  1399
            release_all =  1390
            release_all_but_menu =  1391
            clear_timed_command = 1398
            press_a =  1300
            press_x =  1301
            press_b =  1302
            press_y =  1303
            press_left_side_button =  1304
            press_right_side_button =  1305
            press_left_stick =  1306
            press_right_stick =  1307
            press_menu_right =  1308
            press_menu_left =  1309
            release_dpad =  1310
            press_arrow_north =  1311
            press_arrow_northeast =  1312
            press_arrow_east =  1313
            press_arrow_southeast =  1314
            press_arrow_south =  1315
            press_arrow_southwest =  1316
            press_arrow_west =  1317
            press_arrow_northwest =  1318
            press_xbox_home_button =  1319
            random_axis =  1320
            start_recording =  1321
            set_left_stick_neutral =  1330
            set_left_stick_up =  1331
            set_left_stick_up_right =  1332
            set_left_stick_right =  1333
            set_left_stick_down_right =  1334
            set_left_stick_down =  1335
            set_left_stick_down_left =  1336
            set_left_stick_left =  1337
            set_left_stick_up_left =  1338
            set_right_stick_neutral =  1340
            set_right_stick_up =  1341
            set_right_stick_up_right =  1342
            set_right_stick_right =  1343
            set_right_stick_down_right =  1344
            set_right_stick_down =  1345
            set_right_stick_down_left =  1346
            set_right_stick_left =  1347
            set_right_stick_up_left =  1348
            set_left_stick_horizontal_100 =  1350
            set_left_stick_horizontal_neg_100 =  1351
            set_left_stick_vertical_100 =  1352
            set_left_stick_vertical_neg_100 =  1353
            set_right_stick_horizontal_100 =  1354
            set_right_stick_horizontal_neg_100 =  1355
            set_right_stick_vertical_100 =  1356
            set_right_stick_vertical_neg_100 =  1357
            set_left_trigger_100 =  1358
            set_right_trigger_100 =  1359
            set_left_stick_horizontal_075 =  1360
            set_left_stick_horizontal_neg_075 =  1361
            set_left_stick_vertical_075 =  1362
            set_left_stick_vertical_neg_075 =  1363
            set_right_stick_horizontal_075 =  1364
            set_right_stick_horizontal_neg_075 =  1365
            set_right_stick_vertical_075 =  1366
            set_right_stick_vertical_neg_075 =  1367
            set_left_trigger_075 =  1368
            set_right_trigger_075 =  1369
            set_left_stick_horizontal_050 =  1370
            set_left_stick_horizontal_neg_050 =  1371
            set_left_stick_vertical_050 =  1372
            set_left_stick_vertical_neg_050 =  1373
            set_right_stick_horizontal_050 =  1374
            set_right_stick_horizontal_neg_050 =  1375
            set_right_stick_vertical_050 =  1376
            set_right_stick_vertical_neg_050 =  1377
            set_left_trigger_050 =  1378
            set_right_trigger_050 =  1379
            set_left_stick_horizontal_025 =  1380
            set_left_stick_horizontal_neg_025 =  1381
            set_left_stick_vertical_025 =  1382
            set_left_stick_vertical_neg_025 =  1383
            set_right_stick_horizontal_025 =  1384
            set_right_stick_horizontal_neg_025 =  1385
            set_right_stick_vertical_025 =  1386
            set_right_stick_vertical_neg_025 =  1387
            set_left_trigger_025 =  1388
            set_right_trigger_025 =  1389
    
"""
Example of mapping of the World of Warcraft game use by me when doing bot or twitch play.
"""    

class IntMapping_WarcrafBasicMove:
    
        move_forward:int = WowIntegerKeyboard.numpad_8
        move_backward:int = WowIntegerKeyboard.numpad_5
        move_left:int = WowIntegerKeyboard.numpad_1
        move_right:int = WowIntegerKeyboard.numpad_3
        move_up:int = WowIntegerKeyboard.numpad_2
        move_down:int = WowIntegerKeyboard.numpad_0
        rotate_left:int = WowIntegerKeyboard.numpad_4
        rotate_right:int = WowIntegerKeyboard.numpad_6
        interact:int = WowIntegerKeyboard.numpad_7
        auto_run:int = WowIntegerKeyboard.numpad_9
        open_chat:int = WowIntegerKeyboard.numpad_decimal
        tab:int = WowIntegerKeyboard.tab
        jump:int = WowIntegerKeyboard.space
        power_0:int = WowIntegerKeyboard.alpha_0
        power_1:int = WowIntegerKeyboard.alpha_1
        power_2:int = WowIntegerKeyboard.alpha_2
        power_3:int = WowIntegerKeyboard.alpha_3
        power_4:int = WowIntegerKeyboard.alpha_4
        power_5:int = WowIntegerKeyboard.alpha_5
        power_6:int = WowIntegerKeyboard.alpha_6
        power_7:int = WowIntegerKeyboard.alpha_7
        power_8:int = WowIntegerKeyboard.alpha_8
        power_9:int = WowIntegerKeyboard.alpha_9
        power_extra_0:int = WowIntegerKeyboard.f1
        power_extra_1:int = WowIntegerKeyboard.f2
        power_extra_2:int = WowIntegerKeyboard.f3
        power_extra_3:int = WowIntegerKeyboard.f4
        power_extra_4:int = WowIntegerKeyboard.f5
        power_extra_5:int = WowIntegerKeyboard.f6
        power_extra_6:int = WowIntegerKeyboard.f7
        power_extra_7:int = WowIntegerKeyboard.f8
        power_extra_8:int = WowIntegerKeyboard.f9
        power_extra_9:int = WowIntegerKeyboard.f10
        power_racial_pow:int = WowIntegerKeyboard.f11
        power_mount:int = WowIntegerKeyboard.f12
        # Use of delete is to remind that follow is the best way
        # to show player that you are a bot and will lead to ban.
        # I don't think, it is not use to detected bot but could be at any time.
        follow_target:int = WowIntegerKeyboard.delete 
        map:int = WowIntegerKeyboard.key_m
        # clockwise rotation
        select_group_0:int = WowIntegerKeyboard.arrow_up
        select_group_1:int = WowIntegerKeyboard.arrow_right
        select_group_2:int = WowIntegerKeyboard.arrow_down
        select_group_3:int = WowIntegerKeyboard.arrow_left
        enter:int = WowIntegerKeyboard.enter
        backsapce:int = WowIntegerKeyboard.backspace
        escape:int = WowIntegerKeyboard.escape

"""
Example of mapping of the 10 Seconds Ninja game:
https://store.steampowered.com/app/271670/10_Second_Ninja/
"""
class IntMapping_10SecondsNinja:
    key_sword:int = WowIntegerKeyboard.key_x
    key_shuriken:int = WowIntegerKeyboard.key_z
    key_continue:int = WowIntegerKeyboard.key_c
    key_restart:int = WowIntegerKeyboard.key_r
    key_jump:int = WowIntegerKeyboard.arrow_up
    key_left:int = WowIntegerKeyboard.arrow_left
    key_right:int = WowIntegerKeyboard.arrow_right
    key_enter:int = WowIntegerKeyboard.enter
    key_escape:int = WowIntegerKeyboard.escape
    



        
"""
Find the default int action if you use the Scratch to World of Warcraft standard:
https://github.com/EloiStree/2024_08_29_ScratchToWarcraft
It is based on the Window keystroke index.

"""
class WowIntegerTargetSample:
    
    def __init__(self, ipv4:str = "127.0.0.1", port:int=7073, index:int=0):
        self.wowInteger = SendUdpIID(ipv4, port, index, True)
        
    def jump(self):
        self.wowInteger.push_integer(1032)
        time.sleep(0.1)
        self.wowInteger.push_integer(2032)  

     
    def all_jump(self):
        self.wowInteger.push_integer(0,1032)
        time.sleep(0.1)
        self.wowInteger.push_integer(0,2032)  

    def press_key(self, key:int):
        self.wowInteger.push_integer(key)
    
    def release_key(self, key:int):
        self.wowInteger.push_integer(key+1000)
        
    def press_then_release_key(self, key:int):
        self.wowInteger.push_integer(key)
        self.wowInteger.push_integer(key+1000)
        
    def press_then_release_key_delay(self, key:int, delay:float):
        self.wowInteger.push_integer(key)
        time.sleep(delay)
        self.wowInteger.push_integer(key+1000)
        
    def start_moving_left(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_left)
        
    def stop_moving_left(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_left)
        
    def start_moving_right(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_right)
    
    def stop_moving_right(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_right)
    
    def start_moving_forward(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_forward)
    
    def stop_moving_forward(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_forward)
        
    def start_moving_backward(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_backward)
    
    def stop_moving_backward(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_backward)
    
    def start_moving_up(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_up)
    
    def stop_moving_up(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_up)
    
    def start_moving_down(self):
        self.press_key(IntMapping_WarcrafBasicMove.move_down)
    
    def stop_moving_down(self):
        self.release_key(IntMapping_WarcrafBasicMove.move_down)
        
    def start_rotate_left(self):
        self.press_key(IntMapping_WarcrafBasicMove.rotate_left)
        
    def stop_rotate_left(self):
        self.release_key(IntMapping_WarcrafBasicMove.rotate_left)
        
    def start_rotate_right(self):
        self.press_key(IntMapping_WarcrafBasicMove.rotate_right)
        
    def stop_rotate_right(self):
        self.release_key(IntMapping_WarcrafBasicMove.rotate_right)
        
        
    def start_jump(self):
        self.press_key(IntMapping_WarcrafBasicMove.jump)
    
    def stop_jump(self):
        self.release_key(IntMapping_WarcrafBasicMove.jump)
        
    def start_interact(self):
        self.press_key(IntMapping_WarcrafBasicMove.interact)
        
    def stop_interact(self):
        self.release_key(IntMapping_WarcrafBasicMove.interact)
    
    
    def auto_run(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.auto_run)
    
    def open_chat(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.open_chat)
        
    def tab(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.tab)
        
    def interact(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.interact)
    
    def jump(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.jump)
    
    def power_0(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_0)
    
    def power_1(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_1)
        
    def power_2(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_2)
        
    def power_3(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_3)
    
    def power_4(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_4)
        
    def power_5(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_5)
        
    def power_6(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_6)
    
    def power_7(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_7)
    
    def power_8(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_8)
        
    def power_9(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_9)
    
    def follow(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.follow_target)
        
    def map(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.map)
        
    def mount(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_mount)
        
    def racial_power(self):
        self.press_then_release_key(IntMapping_WarcrafBasicMove.power_racial_pow)
        
    
    
print("Hello World")
player: WowIntegerTargetSample = WowIntegerTargetSample("192.168.1.37",7073,1)

while True:
    
    bool_wow_loop = False
    if bool_wow_loop:
        
        player.press_key(IntMapping_WarcrafBasicMove.tab)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_1)
        time.sleep(1.8)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_2)
        time.sleep(1.8)

    bool_wow_loop_pet = False
    if bool_wow_loop_pet:
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_extra_0)
        player.press_key(IntMapping_WarcrafBasicMove.tab)
        time.sleep(0.1)
        player.press_then_release_key(WowIntegerKeyboard.f1)
        time.sleep(0.1)
        player.press_then_release_key(WowIntegerKeyboard.f10)
        time.sleep(0.1)
        player.press_key(IntMapping_WarcrafBasicMove.tab)
        time.sleep(0.2)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_1)
        time.sleep(1.8)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_2)
        time.sleep(1.8)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_3)
        time.sleep(0.2)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_4)
        time.sleep(1.8)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.power_5)
        time.sleep(1.8)
        player.press_then_release_key(WowIntegerKeyboard.numpad_add)
        time.sleep(0.2)
        player.press_then_release_key(IntMapping_WarcrafBasicMove.interact)
        time.sleep(1.8)
        
    bool_10_seconds_ninja = True
    if bool_10_seconds_ninja:
        
        player.press_then_release_key_delay(IntMapping_10SecondsNinja.key_restart,0.1)
        player.press_key(IntMapping_10SecondsNinja.key_right)
        time.sleep(0.34)
        player.press_then_release_key_delay(IntMapping_10SecondsNinja.key_shuriken,0.1)
        player.press_key(IntMapping_10SecondsNinja.key_jump)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_jump)
        player.release_key(IntMapping_10SecondsNinja.key_right)
        player.press_key(IntMapping_10SecondsNinja.key_left)
        time.sleep(0.05)
        player.press_key(IntMapping_10SecondsNinja.key_jump)
        time.sleep(0.05)
        player.press_key(IntMapping_10SecondsNinja.key_sword)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_sword)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_jump)
        player.release_key(IntMapping_10SecondsNinja.key_left)
        time.sleep(0.24)
        player.press_key(IntMapping_10SecondsNinja.key_jump)
        time.sleep(0.1)
        player.press_key(IntMapping_10SecondsNinja.key_right)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_jump)
        time.sleep(0.1)
        player.press_key(IntMapping_10SecondsNinja.key_jump)
        time.sleep(0.05)
        player.release_key(IntMapping_10SecondsNinja.key_jump)

        time.sleep(0.04)
        player.press_key(IntMapping_10SecondsNinja.key_shuriken)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_shuriken)
        time.sleep(0.1)
        player.release_key(IntMapping_10SecondsNinja.key_right)
        time.sleep(0.5)
        
        
        

    # player.press_key(ScratchToWow_WarcrafBasicMove.move_forward)
    # time.sleep(0.1)
    # player.release_key(ScratchToWow_WarcrafBasicMove.move_forward)
    # time.sleep(1)
    
        
if __name__ == "__main__":
    
    HelloWorldIID.push_my_first_iid()
    HelloWorldIID.console_loop_to_push_iid_apintio()
    
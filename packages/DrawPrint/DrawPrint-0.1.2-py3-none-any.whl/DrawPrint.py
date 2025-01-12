"""winshell定位桌面位置 - hyy制作 - 素材来源于VSCode插件和CSDN - code插件为koroFileHeader"""
"""注意事项:打印的‘狗’可能会看不清"""
"""DrawPrint.py"""
print('')
print('DrawPrint: 0.1.2')

from pyfiglet import Figlet, FigletFont

try:
    import winshell
    import time
    import os
    import turtle as t

except:
    import os
    import time
    os.system('pip install winshell')
    os.system('pip install turtle')
    time.sleep(3)
    import winshell
    import turtle as t

Desktop = winshell.desktop()
os.chdir(Desktop)

def 自制(character,font="larry3d"):
    f = Figlet(font=font)
    print(f.renderText(character))

佛祖镇楼py = [
    '"""',
    '佛祖镇楼:'
    '',
    '                       _oo0oo_',
    '                      o8888888o',
    '                      88" . "88',
    '                      (| -_- |)',
    '                      0\  =  /0',
    "                    ___/`---'\___",
    "                  .' \\|     |// '.",
    "                 / \\|||  :  |||// \ ",
    "                / _||||| -:- |||||- \ ",
    "               |   | \\\  - /// |   |",
    "               | \_|  ''\---/''  |_/ |",
    "               \  .-\__  '-'  ___/-. /",
    "             ___'. .'  /--.--\  `. .'___",
    '          ."" "<  `.___\_<|>_/___." >" "". ',
    '         | | :  `- \`.;`\ _ /`;.`/ - ` : | |',
    '         \  \ `_.   \_ __\ /__ _/   .-` /  /',
    "     =====`-.____`.___ \_____/___.-`___.-'=====",
    "                       `=---='",
    '',
    '          祝：',
    '     程序不出BUG！',
    '"""'
]

def 佛祖镇楼():
    print('')
    print('                       _oo0oo_')
    print('                      o8888888o')
    print('                      88" . "88')
    print('                      (| -_- |)')
    print('                      0\  =  /0')
    print("                    ___/`---'\___")
    print("                  .' \\|     |// '.")
    print("                 / \\|||  :  |||// \ ")
    print("                / _||||| -:- |||||- \ ")
    print("               |   | \\\  - /// |   |")
    print("               | \_|  ''\---/''  |_/ |")
    print("               \  .-\__  '-'  ___/-. /")
    print("             ___'. .'  /--.--\  `. .'___")
    print('          ."" "<  `.___\_<|>_/___." >" "". ')
    print('         | | :  `- \`.;`\ _ /`;.`/ - ` : | |')
    print('         \  \ `_.   \_ __\ /__ _/   .-` /  /')
    print("     =====`-.____`.___ \_____/___.-`___.-'=====")
    print("                       `=---='")
    print('          祝：')
    print('     程序不出BUG！')
    print('')
        
    with open('佛祖镇楼.py','w',encoding='utf-8')as f:
        for lib in 佛祖镇楼py:
            f.write(lib + '\n')

    print('已生成py文件')

笔记本键盘py = [
    '"""',
    '笔记本键盘:',
    '',
    ' ┌─────────────────────────────────────────────────────────────┐',
    ' │┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐│',
    ' ││Esc│!1 │@2 │#3 │$4 │%5 │^6 │&7 │*8 │(9 │)0 │_- │+= │|\ │`~ ││',
    ' │├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┤│',
    ' ││ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{[ │}] │ BS  ││',
    ' │├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤│',
    ' ││ Ctrl │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│"  │ Enter  ││',
    ' │├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────┬───┤│',
    ' ││ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│Shift │Fn ││',
    ' │└─────┬──┴┬──┴──┬┴───┴───┴───┴───┴───┴──┬┴───┴┬──┴┬─────┴───┘│',
    ' │      │Fn │ Alt │         Space         │ Alt │Win│   HHKB   │',
    ' │      └───┴─────┴───────────────────────┴─────┴───┘          │',
    ' └─────────────────────────────────────────────────────────────┘',
    '',
    '          祝：',
    '     程序不出BUG！',
    '',
    '"""'
]

def 笔记本键盘():
    print('')
    print(' ┌─────────────────────────────────────────────────────────────┐')
    print(' │┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐│')
    print(' ││Esc│!1 │@2 │#3 │$4 │%5 │^6 │&7 │*8 │(9 │)0 │_- │+= │|\ │`~ ││')
    print(' │├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┤│')
    print(' ││ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{[ │}] │ BS  ││')
    print(' │├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤│')
    print(' ││ Ctrl │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│"  │ Enter  ││')
    print(' │├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────┬───┤│')
    print(' ││ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│Shift │Fn ││')
    print(' │└─────┬──┴┬──┴──┬┴───┴───┴───┴───┴───┴──┬┴───┴┬──┴┬─────┴───┘│')
    print(' │      │Fn │ Alt │         Space         │ Alt │Win│   HHKB   │')
    print(' │      └───┴─────┴───────────────────────┴─────┴───┘          │')
    print(' └─────────────────────────────────────────────────────────────┘')
    print('')
    print('          祝：')
    print('     程序不出BUG！')
    print('')
    
    with open('笔记本键盘.py','w',encoding='utf-8')as f:
        for lib in 笔记本键盘py:
            f.write(lib + '\n')

    print('已在桌面生成py文件！')

def 狗():
    print('可能会看不清楚:')
    print('')                           
    print('                      :;J7, :,                        ::;7:')
    print('                      ,ivYi, ,                       ;LLLFS:')
    print('                      :iv7Yi                       :7ri;j5PL')
    print('                     ,:ivYLvr                    ,ivrrirrY2X,')
    print('                     :;r@Wwz.7r:                :ivu@kexianli.')
    print('                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur')
    print('                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17')
    print('                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i')
    print('              :,, ,,:   ,::ir@mingyi.irii:i:::j1jri7ZBOS7ivv,')
    print('                 ,::,    ::rv77iiiriii:iii:i::,rvLq@huhao.Li')
    print('             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:')
    print('           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri')
    print('          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:')
    print('        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::')
    print('        :      iuMMP: :,:::,:ii;2GY7OBB0viiii:i:iii:i:::iJqL;::')
    print('       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii')
    print('      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:')
    print('     ,               ,,,,::::i:  @arqiao.       ,:,, ,:::ii;i7:')
    print('    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii')
    print('    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::')
    print('    i,  ,  ,8BMMBBBBBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::')
    print('    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,')
    print('    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:')
    print('    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::')
    print('    :     :rk@Yizero.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,')
    print('     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:i@petermu.,')
    print('          , :r50EZ8MBBBBGOBBBZP7::::i::,:::::,: :,:,::i;rrririiii::')
    print('              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:')
    print('           ,:  :@kevensun.:,:,,,::::i:i:::::,,::::::iir;ii;7v77;ii;i,')
    print('           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiir@xingjief.r;7:i,')
    print('        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::')
    print('         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;@Secbone.ii:::')
    print('')

键盘py = [
    '"""',
    '键盘:',
    ' ┌───┐   ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐ ┌───┬───┬───┐',
    ' │Esc│   │ F1│ F2│ F3│ F4│ │ F5│ F6│ F7│ F8│ │ F9│F10│F11│F12│ │P/S│S L│P/B│  ┌┐    ┌┐    ┌┐',
    ' └───┘   └───┴───┴───┴───┘ └───┴───┴───┴───┘ └───┴───┴───┴───┘ └───┴───┴───┘  └┘    └┘    └┘',
    ' ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐ ┌───┬───┬───┐ ┌───┬───┬───┬───┐',
    ' │~ `│! 1│@ 2│# 3│$ 4│% 5│^ 6│& 7│* 8│( 9│) 0│_ -│+ =│ BacSp │ │Ins│Hom│PUp│ │N L│ / │ * │ - │',
    ' ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤ ├───┼───┼───┤ ├───┼───┼───┼───┤',
    ' │ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{ [│} ]│ | \ │ │Del│End│PDn│ │ 7 │ 8 │ 9 │   ',
    ' ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤ └───┴───┴───┘ ├───┼───┼───┤ + │',
    ' │ Caps │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│"  │ Enter  │               │ 4 │ 5 │ 6 │   │',
    ' ├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────────┤     ┌───┐     ├───┼───┼───┼───┤',
    ' │ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│  Shift   │     │ ↑ │     │ 1 │ 2 │ 3 │   │',
    ' ├─────┬──┴─┬─┴──┬┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤ ┌───┼───┼───┐ ├───┴───┼───┤ E││',
    ' │ Ctrl│    │Alt │         Space         │ Alt│    │    │Ctrl│ │ ← │ ↓ │ → │ │   0   │ . │←─┘│',
    ' └─────┴────┴────┴───────────────────────┴────┴────┴────┴────┘ └───┴───┴───┘ └───────┴───┴───┘',
    '',
    '          祝：',
    '     程序不出BUG！',
    '"""'
]

def 键盘():
    print(' ┌───┐   ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐ ┌───┬───┬───┐')
    print(' │Esc│   │ F1│ F2│ F3│ F4│ │ F5│ F6│ F7│ F8│ │ F9│F10│F11│F12│ │P/S│S L│P/B│  ┌┐    ┌┐    ┌┐')
    print(' └───┘   └───┴───┴───┴───┘ └───┴───┴───┴───┘ └───┴───┴───┴───┘ └───┴───┴───┘  └┘    └┘    └┘')
    print(' ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐ ┌───┬───┬───┐ ┌───┬───┬───┬───┐')
    print(' │~ `│! 1│@ 2│# 3│$ 4│% 5│^ 6│& 7│* 8│( 9│) 0│_ -│+ =│ BacSp │ │Ins│Hom│PUp│ │N L│ / │ * │ - │')
    print(' ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤ ├───┼───┼───┤ ├───┼───┼───┼───┤')
    print(' │ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{ [│} ]│ | \ │ │Del│End│PDn│ │ 7 │ 8 │ 9 │   │')
    print(' ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤ └───┴───┴───┘ ├───┼───┼───┤ + │')
    print(' │ Caps │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│"  │ Enter  │               │ 4 │ 5 │ 6 │   │')
    print(' ├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────────┤     ┌───┐     ├───┼───┼───┼───┤')
    print(' │ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│  Shift   │     │ ↑ │     │ 1 │ 2 │ 3 │   │')
    print(' ├─────┬──┴─┬─┴──┬┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤ ┌───┼───┼───┐ ├───┴───┼───┤ E││')
    print(' │ Ctrl│    │Alt │         Space         │ Alt│    │    │Ctrl│ │ ← │ ↓ │ → │ │   0   │ . │←─┘│')
    print(' └─────┴────┴────┴───────────────────────┴────┴────┴────┴────┘ └───┴───┴───┘ └───────┴───┴───┘')
    print('')
    print('          祝：')
    print('     程序不出BUG！')
    print('')
    
    with open('键盘.py','w',encoding='utf-8')as f:
        for lib in 笔记本键盘py:
            f.write(lib + '\n')

    print('已在桌面生成py文件！')

耶稣py = [
    '"""'
    '耶稣:',
    '',
    '                               |~~~~~~~|',
    "                               |       |",
    "                               |       |",
    "                               |       |",
    "                               |       |",
    "                               |       |",
    "    |~.\\\_\~~~~~~~~~~~~~~xx~~~         ~~~~~~~~~~~~~~~~~~~~~/_//;~|",
    "    |  \  o \_         ,XXXXX),                         _..-~ o /  |",
    "    |    ~~\  ~-.     XXXXX`)))),                 _.--~~   .-~~~   |",
    "     ~~~~~~~`\   ~\~~~XXX' _/ ';))     |~~~~~~..-~     _.-~ ~~~~~~~",
    "              `\   ~~--`_\~\, ;;;\)__.---.~~~      _.-~",
    "                ~-.       `:;;/;; \          _..-~~",
    "                   ~-._      `''        /-~-~",
    "                       `\              /  /",
    "                         |         ,   | |",
    "                          |  '        /  |",
    "                           \/;          |",
    "                            `;   .       |",
    "                            |~~~-----.....|",
    "                           | \             \ ",
    "                          | /\~~--...__    |",
    "                          (|  `\       __-\|",
    "                          ||    \_   /~    |",
    "                          |)     \~-'      |",
    "                           |      | \      '",
    "                           |      |  \    :",
    "                            \     |  |    |",
    "                             |    )  (    )",
    "                              \  /;  /\  |",
    "                              |    |/   |",
    "                              |    |   |",
    "                               \  .'  ||",
    "                               |  |  | |",
    "                               (  | |  |",
    "                               |   \ \ |",
    "                               || o `.)|",
    "                               |`\\) |",
    "                               |       |",
    "                               |       |",
    '',
    '          祝：',
    '     程序不出BUG！',
    '"""'
]

def 耶稣():
    print('                               |~~~~~~~|')
    print('                               |       |')
    print('                               |       |')
    print('                               |       |')
    print('                               |       |')
    print('                               |       |')
    print('    |~.\\\_\~~~~~~~~~~~~~~xx~~~         ~~~~~~~~~~~~~~~~~~~~~/_//;~|')
    print('    |  \  o \_         ,XXXXX),                         _..-~ o /  |')
    print('    |    ~~\  ~-.     XXXXX`)))),                 _.--~~   .-~~~   |')
    print("     ~~~~~~~`\   ~\~~~XXX' _/ ';))     |~~~~~~..-~     _.-~ ~~~~~~~")
    print('              `\   ~~--`_\~\, ;;;\)__.---.~~~      _.-~')
    print('                ~-.       `:;;/;; \          _..-~~')
    print('                   ~-._      `''        /-~-~')
    print('                       `\              /  /')
    print('                         |         ,   | |')
    print("                          |  '        /  |")
    print('                           \/;          |')
    print("                            `;   .       |")
    print('                            |~~~-----.....|')
    print('                           | \             \ ')
    print('                          | /\~~--...__    |')
    print('                          (|  `\       __-\|')
    print('                          ||    \_   /~    |')
    print("                          |)     \~-'      |")
    print("                           |      | \      '")
    print("                           |      |  \    :")
    print("                            \     |  |    |")
    print("                             |    )  (    )")
    print("                              \  /;  /\  |")
    print("                              |    |/   |")
    print('                              |    |   |')
    print("                               \  .'  ||")
    print("                               |  |  | |")
    print("                               (  | |  |")
    print('                               |   \ \ |')
    print('                               || o `.)|')
    print('                               |`\\) |')
    print('                               |       |')
    print('                               |       |')
    print('')
            
    with open('耶稣.py','w',encoding='utf-8')as f:
        for lib in 耶稣py:
            f.write(lib + '\n')

    print('已生成py文件')

龙图腾py = [
    '"""'
    '龙图腾:',
    '......................................&&.........................',
    '....................................&&&..........................',
    '.................................&&&&............................',
    '...............................&&&&..............................',
    '.............................&&&&&&..............................',
    '...........................&&&&&&....&&&..&&&&&&&&&&&&&&&........',
    '..................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&..............',
    '................&...&&&&&&&&&&&&&&&&&&&&&&&&&&&&.................',
    '.......................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.........',
    '...................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...............',
    '..................&&&   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&............',
    '...............&&&&&@  &&&&&&&&&&..&&&&&&&&&&&&&&&&&&&...........',
    '..............&&&&&&&&&&&&&&&.&&....&&&&&&&&&&&&&..&&&&&.........',
    '..........&&&&&&&&&&&&&&&&&&...&.....&&&&&&&&&&&&&...&&&&........',
    '........&&&&&&&&&&&&&&&&&&&.........&&&&&&&&&&&&&&&....&&&.......',
    '.......&&&&&&&&.....................&&&&&&&&&&&&&&&&.....&&......',
    '........&&&&&.....................&&&&&&&&&&&&&&&&&&.............',
    '..........&...................&&&&&&&&&&&&&&&&&&&&&&&............',
    '................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&............',
    '..................&&&&&&&&&&&&&&&&&&&&&&&&&&&&..&&&&&............',
    '..............&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&....&&&&&............',
    '...........&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&......&&&&............',
    '.........&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.........&&&&............',
    '.......&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...........&&&&............',
    '......&&&&&&&&&&&&&&&&&&&...&&&&&&...............&&&.............',
    '.....&&&&&&&&&&&&&&&&............................&&..............',
    '....&&&&&&&&&&&&&&&.................&&...........................',
    '...&&&&&&&&&&&&&&&.....................&&&&......................',
    '...&&&&&&&&&&.&&&........................&&&&&...................',
    '..&&&&&&&&&&&..&&..........................&&&&&&&...............',
    '..&&&&&&&&&&&&...&............&&&.....&&&&...&&&&&&&.............',
    '..&&&&&&&&&&&&&.................&&&.....&&&&&&&&&&&&&&...........',
    '..&&&&&&&&&&&&&&&&..............&&&&&&&&&&&&&&&&&&&&&&&&.........',
    '..&&.&&&&&&&&&&&&&&&&&.........&&&&&&&&&&&&&&&&&&&&&&&&&&&.......',
    '...&&..&&&&&&&&&&&&.........&&&&&&&&&&&&&&&&...&&&&&&&&&&&&......',
    '....&..&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...........&&&&&&&&.....',
    '.......&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&..............&&&&&&&....',
    '.......&&&&&.&&&&&&&&&&&&&&&&&&..&&&&&&&&...&..........&&&&&&....',
    '........&&&.....&&&&&&&&&&&&&.....&&&&&&&&&&...........&..&&&&...',
    '.......&&&........&&&.&&&&&&&&&.....&&&&&.................&&&&...',
    '........&&...................&&&&&&.........................&&&..',
    '.........&.....................&&&&........................&&....',
    '...............................&&&.......................&&......',
    '................................&&......................&&.......',
    '.................................&&..............................',
    '..................................&..............................',
    '',
    '          祝：',
    '     程序不出BUG！',
    '"""'
]

def 龙图腾():
    print('......................................&&.........................')
    print('....................................&&&..........................')
    print('.................................&&&&............................')
    print('...............................&&&&..............................')
    print('.............................&&&&&&..............................')
    print('...........................&&&&&&....&&&..&&&&&&&&&&&&&&&........')
    print('..................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&..............')
    print('................&...&&&&&&&&&&&&&&&&&&&&&&&&&&&&.................')
    print('.......................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.........')
    print('...................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...............')
    print('..................&&&   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&............')
    print('...............&&&&&@  &&&&&&&&&&..&&&&&&&&&&&&&&&&&&&...........')
    print('..............&&&&&&&&&&&&&&&.&&....&&&&&&&&&&&&&..&&&&&.........')
    print('..........&&&&&&&&&&&&&&&&&&...&.....&&&&&&&&&&&&&...&&&&........')
    print('........&&&&&&&&&&&&&&&&&&&.........&&&&&&&&&&&&&&&....&&&.......')
    print('.......&&&&&&&&.....................&&&&&&&&&&&&&&&&.....&&......')
    print('........&&&&&.....................&&&&&&&&&&&&&&&&&&.............')
    print('..........&...................&&&&&&&&&&&&&&&&&&&&&&&............')
    print('................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&............')
    print('..................&&&&&&&&&&&&&&&&&&&&&&&&&&&&..&&&&&............')
    print('..............&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&....&&&&&............')
    print('...........&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&......&&&&............')
    print('.........&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.........&&&&............')
    print('.......&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...........&&&&............')
    print('......&&&&&&&&&&&&&&&&&&&...&&&&&&...............&&&.............')
    print('.....&&&&&&&&&&&&&&&&............................&&..............')
    print('....&&&&&&&&&&&&&&&.................&&...........................')
    print('...&&&&&&&&&&&&&&&.....................&&&&......................')
    print('...&&&&&&&&&&.&&&........................&&&&&...................')
    print('..&&&&&&&&&&&..&&..........................&&&&&&&...............')
    print('..&&&&&&&&&&&&...&............&&&.....&&&&...&&&&&&&.............')
    print('..&&&&&&&&&&&&&.................&&&.....&&&&&&&&&&&&&&...........')
    print('..&&&&&&&&&&&&&&&&..............&&&&&&&&&&&&&&&&&&&&&&&&.........')
    print('..&&.&&&&&&&&&&&&&&&&&.........&&&&&&&&&&&&&&&&&&&&&&&&&&&.......')
    print('...&&..&&&&&&&&&&&&.........&&&&&&&&&&&&&&&&...&&&&&&&&&&&&......')
    print('....&..&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...........&&&&&&&&.....')
    print('.......&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&..............&&&&&&&....')
    print('.......&&&&&.&&&&&&&&&&&&&&&&&&..&&&&&&&&...&..........&&&&&&....')
    print('........&&&.....&&&&&&&&&&&&&.....&&&&&&&&&&...........&..&&&&...')
    print('.......&&&........&&&.&&&&&&&&&.....&&&&&.................&&&&...')
    print('.......&&&...............&&&&&&&.......&&&&&&&&............&&&...')
    print('........&&...................&&&&&&.........................&&&..')
    print('.........&.....................&&&&........................&&....')
    print('...............................&&&.......................&&......')
    print('................................&&......................&&.......')
    print('.................................&&..............................')
    print('..................................&..............................')
    print('')
    print('          祝：')
    print('     程序不出BUG！')
    print('')
            
    with open('龙图腾.py','w',encoding='utf-8')as f:
        for lib in 龙图腾py:
            f.write(lib + '\n')

    print('已生成py文件')

"""后面的是turtle画的了"""
def B站小电视():
    #边框
    t.pu()
    t.goto(-250,-225)
    t.pd()
    t.pensize(15)
    for i in range(2):
        t.fd(500)
        t.circle(50,90)
        t.fd(350)
        t.circle(50,90)
    #嘴巴
    t.pu()
    t.goto(-100,-50)
    t.seth(270)
    t.pd()
    t.pensize(15)
    t.circle(50,180)
    t.seth(270)
    t.circle(50,180)
    #左眼
    t.pu()
    t.goto(-200,50)
    t.seth(30)
    t.pd()
    t.pensize(20)
    t.fd(150)
    #右眼
    t.pu()
    t.goto(200,50)
    t.seth(150)
    t.pd()
    t.pensize(20)
    t.fd(150)
    #左天线
    t.pu()
    t.goto(-100,230)
    t.seth(135)
    t.pd()
    t.pensize(30)
    t.fd(150)
    #右天线
    t.pu()
    t.goto(100,230)
    t.seth(45)
    t.pd()
    t.pensize(30)
    t.fd(150)
    #左脚
    t.pu()
    t.goto(-150,-225)
    t.seth(270)
    t.pd()
    t.pensize(15)
    t.circle(30,180)
    #右脚
    t.pu()
    t.goto(90,-225)
    t.seth(270)
    t.pd()
    t.pensize(15)
    t.circle(30,180)
    t.exitonclick()

def Python图标():
    t.colormode(255)
    t.speed(10)
    t.pensize(3)
    t.pu()
    t.goto(-200,105)
    # 蓝色区域
    t.pencolor(54,110,157)
    t.fillcolor(54,110,157)
    t.begin_fill()
    t.goto(-225,-115)
    t.pd()
    t.seth(90)
    t.fd(55)
    t.circle(-50,90)
    t.fd(190)
    t.circle(50,90)
    t.fd(100)
    t.circle(85,90)
    t.fd(100)
    t.circle(85,90)
    t.fd(30)
    t.left(90)
    t.fd(150)
    t.seth(270)
    t.fd(20)
    t.right(90)
    t.fd(220)
    t.circle(50,90)
    t.fd(105)
    t.circle(50,90)
    t.fd(50)
    t.left(90)
    t.end_fill()
    t.fillcolor(255,255,255)
    t.pu()
    t.goto(-125,155)
    t.pd()
    t.pencolor(255,255,255)
    t.begin_fill()
    t.circle(20,360)
    t.end_fill()
    # 黄色区域
    t.pu()
    t.goto(85,80)
    t.pd()
    t.pencolor(255,212,69)
    t.fillcolor(255,212,69)
    t.begin_fill()
    t.seth(270)
    t.fd(55)
    t.circle(-50,90)
    t.fd(190)
    t.circle(50,90)
    t.fd(100)
    t.circle(85,90)
    t.fd(100)
    t.circle(85,90)
    t.fd(30)
    t.left(90)
    t.fd(150)
    t.right(90)
    t.fd(20)
    t.right(90)
    t.fd(220)
    t.circle(50,90)
    t.fd(105)
    t.circle(50,90)
    t.fd(50)
    t.end_fill()
    t.fillcolor(255,255,255)
    t.pu()
    t.goto(-10,-180)
    t.pd()
    t.pencolor(255,255,255)
    t.begin_fill()
    t.circle(20,360)
    t.end_fill()
    t.done()

def 太极图():
    import turtle
    
    angle = 270
    
    def tai():
        r = 200  # 设置半径
        turtle.penup()  # 拿起画笔
        turtle.goto(0, 0)  # 到画布中心
        turtle.setheading(angle)  # 设置当前朝向为angle角度
        turtle.fd(r)  # 前进r的距离
        turtle.pendown()  # 放下画笔
        turtle.right(90)  # 调整海龟角度
    
        # 画阳鱼
        turtle.fillcolor("white")
        turtle.begin_fill()  # 开始填充
        turtle.circle(-r / 2, 180)
        turtle.circle(r / 2, 180)
        turtle.circle(r, 180)
        turtle.end_fill()
    
        # 画阴鱼
        turtle.fillcolor("black")
        turtle.begin_fill()
        turtle.circle(r, 180)
        turtle.right(180)
        turtle.circle(-r / 2, 180)
        turtle.circle(r / 2, 180)
        turtle.end_fill()
    
        # 画阴鱼眼
        turtle.penup()
        turtle.setheading(angle)
        turtle.fd(-r / 2)
        turtle.pendown()
        turtle.dot(r / 4, "white")
    
        # 画阳鱼眼
        turtle.penup()
        turtle.fd(-r)
        turtle.pendown()
        turtle.dot(r / 4, "black")
        turtle.penup()
    
    turtle.tracer(0)
    for i in range(10000000):
        tai()
        turtle.update()
        turtle.clear()
        angle += 1

def 奥运五环():
    import turtle 

    def draw_a_circle(x, y, color, radius=70, pensize=10):
        turtle.penup()
        turtle.goto(x, y)
        turtle.pensize(pensize)
        turtle.pencolor(color)
        turtle.pendown()
        turtle.circle(radius)
        turtle.penup()

    circles = [
        (-130, 75, "blue"),
        (-10, 75, "black"),
        (110, 75, "red"),
        (-60, -20, "yellow"),
        (60, -20, "green")
    ]

    for x, y, color in circles:
        draw_a_circle(x, y, color)

    turtle.done()

from turtle import *
def 雷达图(select):
    if select == 1:
        import matplotlib.pyplot as plt
        import numpy as np
        values = [0.09,-0.05,0.20,-0.02,0.08,0.09,0.03,0.027]
        x = np.linspace(0,2*np.pi,9)[:-1]
        c = np.random.random(size=(8,3))
        fig = plt.figure()
        plt.axes(polar=True)
        #获取当前的axes
        print(plt.gca())
        #绘图
        plt.bar(x,values,width=0.5,color=c,align='center')
        plt.scatter(x,values,marker='o',c='black')
        #添加文本
        plt.figtext(0.03,0.7,s='陆地面积增长指数',fontproperties='KaiTi',fontsize=22,rotation='vertical',verticalalignment='center',horizontalalignment='center')
        plt.ylim(-0.05, 0.25)
        labels = np.array(['省1','省2','省3','省4','省5','省6','省7','研究区'])
        dataLength = 8
        angles = np.linspace(0, 2*np.pi, dataLength, endpoint=False)
        plt.thetagrids(angles * 180/np.pi, labels,fontproperties='KaiTi',fontsize=18)
        #添加注释
        # plt.annotate(s='省',xy=(0,0.09),xytext=(0,0.28),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='省',xy=(0,-0.05),xytext=(np.pi/4,0.28),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='省',xy=(0,0.20),xytext=(np.pi/2,0.28),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='省',xy=(0,-0.02),xytext=(3*np.pi/4,0.33),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='省',xy=(0,0.08),xytext=(np.pi,0.38),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='省',xy=(0,0.09),xytext=(np.pi*5/4,0.35),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='前江省',xy=(0,0.03),xytext=(np.pi*3/2,0.30),fontproperties='KaiTi',fontsize=18)
        # plt.annotate(s='研究区',xy=(0,0.027),xytext=(np.pi*7/4,0.28),fontproperties='KaiTi',fontsize=18)
        #设置网格线样式
        plt.grid(c='gray',linestyle='--',)
        # y1 = [-0.05,0.0,0.05,0.10,0.15,0.20,0.25]
        # lai=fig.add_axes([0.12,0.01,0.8,0.98])
        # lai.patch.set_alpha(0.25)
        # lai.set_ylim(-0.05, 0.25)
        #显示
        plt.show()

    if select == 2:
        import matplotlib.pyplot as plt
        import numpy as np
        plt.rcParams['font.sans-serif'] = ['SimHei'] # 图例中文问题
        plt.rcParams['axes.unicode_minus'] = False #正负号问题
        x= np.array(['1省','2省','3省','4省','5省','6省','7省','研究区'])
        y1 = np.array([5.5, 7.2, 17.3, 15.0, 10.8, 21.8, 3.4, 81.4])
        y2 = [0, -27.5, -3.9, -18.0, -0.2, -1.4, -1.7, -52.1]
        y3 = [5.5, -20.2, 13.4, -2.9, 10.6, 20.4, 1.7, 28.5]
        loc=[0.12,0.15,0.65,0.6]
        plt.axes(loc)
        plt.bar(x,y1,0.4,label=u'退')
        plt.bar(x,y2,0.4,label=u'进')
        plt.plot(x,y3,marker='o',markersize='6',c='black')
        y=np.array([-50, 0 ,50])
        plt.xticks(x,fontproperties='KaiTi',fontsize=8)
        plt.yticks(y)
        plt.grid(c='gray',linestyle='--',alpha=0.25)
        plt.figtext(0.02,0.45,s='变化（km2）',fontproperties='KaiTi',fontsize=14,rotation='vertical',verticalalignment='center',horizontalalignment='center')
        #frameon=False 去掉图例边框
        plt.legend(loc='center', bbox_to_anchor=(1.2, 0.5),ncol=1,
        frameon=False)
        plt.show()

    else:
        print("\033[91mERROR: 我们无法识别您输入的代码.\033[0m")

from random import *
from turtle import *

def 皮卡丘():
    import turtle as t
    
    def infoPrt():
        print('coordinate: ' + str(t.pos()))
        print('angle: ' + str(t.heading()))
    
    t.pensize(3)
    t.hideturtle() 
    t.colormode(255)
    t.color("black")
    t.setup(700, 650)
    t.speed(1)
    t.st()
    #t.dot()
    t.pu()  #提起笔移动
    #t.goto(-150,100)
    t.goto(-210,86)
    t.pd()
    infoPrt()
    # 头
    print('头')
    t.seth(85)
    t.circle(-100,50)
    #t.seth(78)
    #t.circle(-100,25)
    infoPrt()
    t.seth(25)
    t.circle(-170,50)
    infoPrt()
    
    # 右耳
    print('右耳')
    t.seth(40)
    #t.circle(-250,52)
    t.circle(-250,30)
    infoPrt()
    # 右耳尖
    t.begin_fill()
    # 左
    t.circle(-250,22)
    #t.fillcolor("pink")
    # 右
    t.seth(227)
    t.circle(-270, 15)
    prePos = t.pos()
    infoPrt()
    # 下
    t.seth(105)
    t.circle(100, 32)
    t.end_fill()
    t.pu()
    t.setpos(prePos)
    t.pd()
    t.seth(212)
    t.circle(-270, 28)
    prePos = t.pos()
    t.pu()
    t.goto(t.xcor()+5,t.ycor()-2)
    t.pd()
    # 躯干
    print('躯干')
    t.seth(280)
    t.circle(500, 30)
    infoPrt()
    # 臀部
    print('臀部')
    t.seth(120)
    #t.circle(150, -55)
    t.circle(150, -11)
    p_tail=t.pos()
    t.circle(150, -44)
    p_butt=t.pos()
    infoPrt()
    # 尾巴
    t.pu()
    t.setpos(p_tail)
    t.pd()
    t.begin_fill()
    t.seth(50)
    t.fd(25)
    t.seth(-50)
    t.fd(30)
    p_tail1=t.pos
    t.seth(-140)
    t.fd(36)
    t.end_fill()
    t.seth(39)
    # 右尾和h1
    t.fd(72)
    # 右尾和v1
    t.seth(125)
    t.fd(48)
    # 右尾和h2
    t.seth(40)
    t.fd(53)
    # 右尾和v2
    t.seth(88)
    t.fd(45)
    # 右尾和h3
    t.seth(35)
    t.fd(105)
    # 右尾和v3
    t.seth(105)
    t.circle(850, 8)
    #t.fd(105)
    t.seth(215)
    #t.fd(125)
    t.circle(850, 11)
    t.seth(280)
    t.fd(110)
    t.seth(220)
    t.fd(50)
    t.seth(309)
    t.fd(56)
    
    # 底盘
    print('底盘')
    t.pu()
    t.setpos(p_butt)
    t.pd()
    t.seth(20)
    t.circle(120, -45)
    infoPrt()
    
    t.seth(330)
    t.circle(-150, -30)
    infoPrt()
    prePos = t.pos()
    t.pu()
    t.goto(t.xcor()+20,t.ycor())
    t.pd()
    t.seth(230)
    t.circle(-70, 120)
    p_bot=t.pos()
    # 两脚-right
    t.pu()
    t.setpos(p_butt)
    t.setpos(t.xcor()+5,t.ycor()+5)
    t.pd()
    t.seth(-86)
    t.fd(30)
    t.seth(-93)
    t.fd(33)
    t.seth(-225)
    t.circle(-150, 22)
    # 两脚-left
    t.pu()
    t.setpos(p_bot)
    t.setpos(t.xcor()+85,t.ycor()-43)
    t.pd()
    t.seth(-105)
    t.fd(50)
    t.seth(-225)
    t.circle(-150, 22)
    # 左躯干
    print('躯干')
    t.pu()
    t.setpos(p_bot)
    t.pd()
    t.seth(90)
    t.circle(450, 13)
    p_lfhd = t.pos()
    t.circle(450, 5)
    t.pu()
    t.circle(450, 5)
    t.pd()
    t.circle(450, 6)
    infoPrt()
    # 左脸
    t.begin_fill()
    t.fillcolor("pink")
    print('左脸')
    t.seth(330)
    t.circle(50, -90)
    infoPrt()
    # 左酒窝
    t.seth(30)
    t.circle(-15, 120)
    t.seth(-70)
    t.circle(-30, 90)
    t.end_fill()
    # 左手
    t.pu()
    t.setpos(p_lfhd)
    t.pd()
    t.seth(160)
    t.circle(150, 30)
    infoPrt()
    t.seth(180)
    t.circle(-30, 150)
    t.fd(67)
    t.pu()
    t.setpos(t.xcor()-40,t.ycor()-60)
    t.pd()
    t.seth(200)
    t.circle(-5, 180)
    # 右手
    t.pu()
    t.setpos(p_lfhd)
    t.setpos(t.xcor()+180,t.ycor()+5)
    t.pd()
    t.seth(200)
    t.circle(-50, 100)
    t.pu()
    t.circle(-50, 15)
    t.pd()
    t.circle(-50, 65)
    t.pu()
    t.setpos(t.xcor()+10,t.ycor()-45)
    t.pd()
    #t.seth(270)
    #t.circle(-30, -180)
    t.seth(80)
    t.fd(10)
    t.seth(165)
    t.circle(10, 60)
    t.seth(90)
    t.fd(5)
    t.seth(165)
    t.circle(10, 60)
    t.seth(95)
    t.fd(5)
    t.seth(185)
    t.circle(10, 60)
    t.seth(105)
    t.fd(10)
    t.seth(230)
    t.fd(20)
    t.seth(145)
    t.fd(10)
    t.seth(285)
    t.fd(20)
    # 右酒窝
    t.begin_fill()
    t.fillcolor("pink")
    t.pu()
    t.setpos(t.xcor()-40,t.ycor()+110)
    t.pd()
    t.circle(27, 360)
    t.end_fill()
    #x-20 ,y+50
    """画嘴"""
    color("black", "#F35590")
    # 下嘴弧度并填充颜色
    penup()
    goto(-100, 72)
    pendown()
    begin_fill()
    setheading(260)
    forward(60)
    circle(-11, 150)
    forward(55)
    print(position())
    penup()
    goto(-128.46, 71.97)
    pendown()
    end_fill()
    #嘴中最上方的阴影部分
    color("#6A070D", "#6A070D")
    begin_fill()
    penup()
    goto(-99.00, 72.00)
    pendown()
    penup()
    goto(-104.29, 48.3)
    pendown()
    penup()
    goto(-142, 45)
    pendown()
    penup()
    goto(-150.40, 62.74)
    pendown()
    penup()
    goto(-128.46, 71.97)
    pendown()
    penup()
    goto(-99.00, 72.00)
    pendown()
    end_fill()
    #上嘴唇
    color("black","#FFD624")
    penup()
    goto(-168, 65)
    pendown()
    begin_fill()
    setheading(-25)
    for i in range(2):
        setheading(-25)
        circle(35, 70)
    end_fill()
    #嘴中第二个阴影部分
    color("#AB1945", "#AB1945")
    penup()
    goto(-142, 45)
    pendown()
    begin_fill()
    setheading(40)
    circle(-33, 70)
    goto(-104,48.3)
    penup()
    goto(-108,33)
    pendown()
    setheading(155)
    circle(25, 70)
    end_fill()
    
    # 左眼
    t.pu()
    t.color("black")
    t.setpos(t.xcor()-40,t.ycor()+90)
    t.pd()
    t.circle(5)
    t.pu()
    t.setpos(t.xcor()+5,t.ycor()+10)
    t.pd()
    t.begin_fill()
    t.seth(190)
    t.circle(15, 130)
    t.seth(310)
    t.circle(10, 15)
    t.seth(0)
    t.circle(17, 133)
    t.seth(90)
    t.circle(10, 15)
    t.end_fill()
    t.pu()
    t.setpos(t.xcor()+2,t.ycor()-15)
    t.pd()
    t.color("white")
    t.begin_fill()
    t.circle(5)
    t.end_fill()
    # 右眼
    t.pu()
    t.setpos(t.xcor()+85,t.ycor()+15)
    t.pd()
    t.color("black")
    t.circle(5)
    t.pu()
    t.setpos(t.xcor()+5,t.ycor()+10)
    t.pd()
    t.begin_fill()
    t.seth(190)
    t.circle(20, 130)
    t.seth(310)
    t.circle(10, 15)
    t.seth(0)
    t.circle(22, 133)
    t.seth(90)
    t.circle(13, 15)
    t.end_fill()
    t.pu()
    t.setpos(t.xcor()-7,t.ycor()-15)
    t.pd()
    t.color("white")
    t.begin_fill()
    t.circle(7)
    t.end_fill()
    # 左耳
    t.color("black")
    t.pu()
    t.goto(-210,86)
    t.setpos(t.xcor()+15,t.ycor()+38)
    t.pd()
    t.seth(90)
    t.circle(-250,30)
    t.begin_fill()
    # 左
    t.circle(-250,18)
    # 右
    t.seth(270)
    t.circle(-270, 12)
    prePos = t.pos()
    # 下
    t.seth(180)
    t.circle(100, 30)
    t.end_fill()
    t.pu()
    t.setpos(prePos)
    t.pd()
    t.seth(270)
    t.circle(-270, 18)
    t.screensize(50,50,bg='yellow')
    # 输出文字
    printer = t.Turtle()
    printer.hideturtle()
    printer.penup()
    printer.goto(-350,-100)
    printer.write("皮\n\n",move = True, align="left", font=("楷体", 30, "bold"))
    printer.goto(-350,-150)
    printer.write("卡\n\n",move = True, align="left", font=("楷体", 30, "bold"))
    printer.goto(-350,-200)
    printer.write("丘\n\n",move = True, align="left", font=("楷体", 30, "bold"))
    printer.goto(-350,-250)
    printer.write("！！\n\n",move = True, align="left", font=("楷体", 30, "bold"))
    自制('PiKaQiu!')
    t.hideturtle()
    t.done()

def 蜡笔小新():
    '''设置'''
    t.setup(800,500)
    t.pensize(2)
    t.colormode(255)
    t.speed(7)  # 绘画速度
    t.color('black',(255,228,181))
    #t.shape('turtle')
    t.speed(5)
    t.showturtle()
    # 头
    t.pu()
    t.goto(-150,10)
    t.pd()
    t.seth(0)
    t.begin_fill()
    t.left(135)
    t.circle(-70,85)
    t.right(8)
    t.circle(-85,44)
    t.left(10)
    t.circle(40,61)
    t.right(15)
    t.fd(20)
    t.right(5)
    t.circle(-40,45)
    t.left(6)
    t.circle(-70,25)
    t.left(18)
    t.circle(-80,35)
    t.left(10)
    t.circle(-70,27)
    t.circle(-120,54)
    
    # 耳朵
    t.pu()
    t.goto(82,30)
    t.pd()
    t.left(140)
    t.fd(20)
    t.right(10)
    t.circle(-20,65)
    t.seth(-50)
    t.fd(5)
    t.right(13)
    t.circle(-50,50)
    t.right(10)
    t.circle(-60,25)
    t.right(7)
    t.circle(-50,20)
    t.circle(-10,90)
    
    # 补充完整头部
    t.pu()
    t.goto(-150,10)
    t.pd()
    t.color('black',(255,228,181))
    t.right(130)
    t.circle(90,33)
    t.right(16)
    t.circle(370,28)
    t.end_fill()
    
    # 头发
    t.color('black','black')
    t.pu()
    t.goto(-18,180)
    t.pd()
    t.begin_fill()
    t.right(30)
    t.circle(-350,19)
    t.right(38)
    t.circle(-300,17)
    t.left(135)
    t.fd(23)
    t.left(39)
    t.circle(120,63)
    t.left(10)
    t.circle(110,28)
    t.right(11)
    t.circle(85,14)
    t.end_fill()
    
    #眉毛
    t.pu()
    t.goto(-52,151)
    t.pd()
    t.begin_fill()
    t.right(205)
    t.circle(110,33)
    t.circle(7,130)
    t.left(50)
    t.circle(-110,30)
    t.circle(8,140)
    t.end_fill()
    t.pu()
    t.goto(48,140)
    t.pd()
    t.begin_fill()
    t.right(4)
    t.circle(150,18)
    t.right(4)
    t.circle(-6,140)
    t.right(28)
    t.circle(-150,19)
    t.right(10)
    t.circle(-10,150)
    t.end_fill()
    t.pu()
    t.goto(-69,126)
    t.pd()
    t.left(70)
    t.circle(-80,37)
    t.right(15)
    t.circle(-25,100)
    t.pu()
    t.goto(2,91)
    t.pd()
    t.left(150)
    t.circle(-70,30)
    t.right(10)
    t.circle(-40,60)
    t.circle(-70,20)
    
    #眼睛
    t.pu()
    t.goto(-60,110)
    t.pd()
    t.begin_fill()
    t.right(52)
    t.circle(27)
    t.end_fill()
    t.color('black','white')
    t.pu()
    t.goto(-45,110)
    t.pd()
    t.begin_fill()
    t.right(24)
    t.circle(20,80)
    t.circle(7,100)
    t.seth(40)
    t.fd(22)
    t.left(17)
    t.circle(10,155)
    t.end_fill()
    t.pu()
    t.goto(-20,95)
    t.pd()
    t.begin_fill()
    t.left(70)
    t.circle(-14,80)
    t.circle(-7,120)
    t.right(44)
    t.circle(35,30)
    t.end_fill()
    t.pu()
    t.goto(-41,77)
    t.pd()
    t.begin_fill()
    t.left(28)
    t.circle(6)
    t.end_fill()
    t.color('black','black')
    t.pu()
    t.goto(-5,55)
    t.pd()
    t.begin_fill()
    t.left(10)
    t.circle(-25)
    t.end_fill()
    t.color('black','white')
    t.pu()
    t.goto(5,57)
    t.pd()
    t.begin_fill()
    t.left(40)
    t.circle(-8,120)
    t.left(30)
    t.circle(-19,80)
    t.circle(-8,120)
    t.right(32)
    t.circle(19,60)
    t.right(55)
    t.circle(-9,95)
    t.end_fill()
    t.pu()
    t.goto(38,62)
    t.pd()
    t.begin_fill()
    t.left(190)
    t.circle(-15,50)
    t.circle(-8,100)
    t.right(40)
    t.circle(-10,80)
    t.end_fill()
    t.pu()
    t.goto(10,50)
    t.pd()
    t.begin_fill()
    t.circle(-5)
    t.end_fill()
    
    #嘴巴
    t.pu()
    t.goto(-129,12)
    t.pd()
    t.circle(-40,35)
    #身体
    t.color('black',(205,32,32))
    t.pu()
    t.goto(-142,7)
    t.pd()
    t.begin_fill()
    t.seth(-150)
    t.fd(18)
    t.seth(150)
    t.fd(55)
    t.left(105)
    t.circle(-43,40)
    t.right(125)
    t.circle(-43,30)
    t.left(180)
    t.circle(43,30)
    t.seth(-50)
    t.fd(46)
    t.circle(50,26)
    t.left(27)
    t.circle(60,50)
    t.right(180)
    t.circle(100,60)
    t.seth(0)
    t.fd(194)
    t.left(120)
    t.circle(-50,50)
    t.fd(25)
    t.right(20)
    t.circle(34,66)
    t.circle(18,116)
    t.right(30)
    t.circle(-90,18)
    t.seth(135)
    t.fd(12)
    t.seth(-145)
    t.fd(10)
    t.right(46)
    t.circle(-90,20)
    t.circle(10,100)
    t.circle(-60,20)
    t.right(130)
    t.circle(-50,20)
    t.left(90)
    t.circle(-370,6)
    t.left(15)
    t.circle(-90,13)
    t.right(7)
    t.circle(-90,18)
    t.end_fill()
    t.pu()
    t.goto(-64,-33)
    t.pd()
    t.left(160)
    t.circle(100,40)
    t.circle(40,40)
    
    #手
    t.color('black',(255,228,181))
    t.pu()
    t.goto(-62,-28)
    t.pd()
    t.begin_fill()
    t.seth(140)
    t.fd(8)
    t.left(77)
    t.circle(-12,150)
    t.left(90)
    t.fd(11)
    t.circle(-4,120)
    t.right(45)
    t.fd(11)
    t.left(130)
    t.circle(20,35)
    t.circle(-4,140)
    t.right(30)
    t.circle(-20,40)
    t.left(160)
    t.circle(20,40)
    t.circle(-4,140)
    t.right(20)
    t.circle(-20,50)
    t.left(190)
    t.circle(-20,40)
    t.circle(-3,130)
    t.left(5)
    t.circle(-20,60)
    t.left(180)
    t.circle(-20,40)
    t.seth(25)
    t.fd(10)
    t.left(240)
    t.circle(-30,30)
    t.left(40)
    t.circle(60,20)
    t.seth(-30)
    t.fd(7)
    t.seth(-125)
    t.fd(25)
    t.end_fill()
    t.pu()
    t.goto(-212,3)
    t.pd()
    t.begin_fill()
    t.seth(150)
    t.fd(12)
    t.left(90)
    t.fd(8)
    t.right(50)
    t.circle(-9,90)
    t.left(110)
    t.fd(14)
    t.right(40)
    t.circle(-4,120)
    t.right(15)
    t.circle(-20,40)
    t.left(180)
    t.circle(-3,100)
    t.left(123)
    t.circle(-30,30)
    t.circle(-3,150)
    t.right(10)
    t.circle(-30,30)
    t.seth(80)
    t.fd(3)
    t.left(72)
    t.circle(30,30)
    t.right(8)
    t.circle(-4,120)
    t.right(43)
    t.circle(-30,40)
    t.seth(80)
    t.fd(3)
    t.left(70)
    t.circle(30,34)
    t.right(17)
    t.circle(-4,120)
    t.right(27)
    t.circle(-20,90)
    t.left(180)
    t.circle(-20,50)
    t.seth(35)
    t.fd(8)
    t.left(234)
    t.circle(60,20)
    t.seth(-33)
    t.circle(-50,23)
    t.seth(-119)
    t.fd(16)
    t.end_fill()
    自制('LaBiXiaoXin!')
    t.done()

def 简易魔法阵():
    import turtle
    turtle.screensize(600,600,"black")
    turtle.hideturtle()

    #最外圈圆
    turtle.pensize("8")
    turtle.pencolor("white")
    turtle.speed(0)
    turtle.penup()
    turtle.goto(0,250)
    turtle.pendown()
    turtle.circle(-250)


    turtle.pensize("4")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,243)
    turtle.pendown()
    turtle.circle(-243,steps=7)

    #第二圈七边形
    turtle.pensize("1")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,233)
    turtle.pendown()
    turtle.circle(-233,steps=7)

    #七边形对角线
    turtle.pensize("7")
    turtle.pencolor("white")
    turtle.speed(6)
    turtle.penup()
    turtle.goto(1,228)
    turtle.pendown()
    turtle.seth(0)

    turtle.right(51.6)
    turtle.forward(100) #356
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    turtle.right(102.8)
    turtle.forward(100)
    turtle.penup()
    turtle.forward(20)
    turtle.pendown()
    turtle.forward(236)

    #t2_1.qibiao()

    #小七边形
    turtle.pensize("3")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(-64,134)
    turtle.pendown()
    turtle.seth(25.5)
    turtle.circle(-149,steps=7)

    #第二圈圆
    turtle.pensize("2")
    turtle.pencolor("white")
    turtle.speed(0)
    turtle.penup()
    turtle.goto(0,128)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-128)

    """
    turtle.pensize("1")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,127)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-126,steps=6)
    """

    #第3个圆
    turtle.pensize("1")
    turtle.pencolor("white")
    turtle.speed(0)
    turtle.penup()
    turtle.goto(0,80)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-80)



    #第二圈圆的周围五个圆
    turtle.speed(0)
    turtle.penup()
    turtle.goto(0,127)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-24)

    turtle.speed(0)
    turtle.penup()
    turtle.goto(110,65)
    turtle.pendown()
    turtle.seth(-60)
    turtle.circle(-24)

    turtle.speed(0)
    turtle.penup()
    turtle.goto(110,-63)
    turtle.pendown()
    turtle.seth(-120)
    turtle.circle(-24)

    turtle.speed(0)
    turtle.penup()
    turtle.goto(0,-126)
    turtle.pendown()
    turtle.seth(-180)
    turtle.circle(-24)

    turtle.speed(0)
    turtle.penup()
    turtle.goto(-110,-63)
    turtle.pendown()
    turtle.seth(-240)
    turtle.circle(-24)

    turtle.speed(0)
    turtle.penup()
    turtle.goto(-110,65)
    turtle.pendown()
    turtle.seth(-300)
    turtle.circle(-24)


    #正三角
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,103)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-102,steps =3)

    #倒三角
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,-102)
    turtle.pendown()
    turtle.seth(-180)
    turtle.circle(-102,steps =3)

    """
    turtle.penup()
    turtle.goto(0,90)
    turtle.pendown()
    """
    #第4个圆
    turtle.pensize("3")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,40)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-40)

    #圆内五角星
    #t2_1.wjx(-35,12,70,24,9,2)

    """
    turtle.pensize("1")
    turtle.pencolor("white")
    turtle.speed(10)
    turtle.penup()
    turtle.goto(0,80)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-80,steps=3)
    """
    #圆边三个箭头
    turtle.pensize("1")
    turtle.pencolor("white")
    turtle.speed(0)

    turtle.penup()
    turtle.goto(-18,38)
    turtle.pendown()
    turtle.seth(67)
    turtle.forward(47)
    turtle.right(134)
    turtle.forward(49)


    turtle.penup()
    turtle.goto(-40,-3)
    turtle.pendown()
    turtle.seth(-128)
    turtle.forward(47)
    turtle.left(134)
    turtle.forward(49)

    turtle.penup()
    turtle.goto(40,-3)
    turtle.pendown()
    turtle.seth(-52)
    turtle.forward(47)
    turtle.right(134)
    turtle.forward(49)
    自制('MoFaZhen!')
    turtle.done()

def 月饼():
    import turtle
    #调用turtle库
    t = turtle.Pen()  # 画笔一 用于画图
    t.speed(0)
    
    
    # 花纹颜色 #F29407
    # 饼身颜色 #F8B41A
    
    # 画 饼身部分
    def outfill_flower(flower_num: "花瓣数量", flower_color: "花瓣颜色"):
        for i in range(flower_num):
            t.left(i * (360 // flower_num))
            t.color(flower_color)
            t.penup()
            t.forward(200)
            t.pendown()
            t.fillcolor(flower_color)
            t.begin_fill()
            t.circle(60)
            t.end_fill()
            t.penup()
            t.home()
    
    
    # 画 饼身外围 花纹部分
    def out_line_flower(flower_num: "花纹数量", flower_color: "花纹颜色"):
        for i in range(flower_num):
            t.pensize(5)
            t.left(i * (360 // 18))
            t.color(flower_color)
            t.penup()
            t.forward(192)
            t.pendown()
            t.circle(60)
            t.penup()
            t.home()
    
    
    # 画内测的大圆 大圆的填充色比饼身略亮
    def big_circle(circle_color: "大圆颜色", circle_fill_color: "大圆填充颜色", circle_size: "大圆半径"):
        t.goto(circle_size, 0)
        t.left(90)
        t.pendown()
        t.pensize(8)
        t.color(circle_color)
        t.fillcolor(circle_fill_color)
        t.begin_fill()
        t.circle(circle_size)
        t.end_fill()
        t.penup()
        t.home()
    
    
    # 饼上印花文字 文字内容和坐标用字典存储
    def write_font(text_content: "文本内容", text_color: "文本颜色", size: "文字大小"):
        t.color(text_color)
        for x in text_content:
            t.penup()
            t.goto(text_content[x])
            t.write(x, align='center', font=('simhei', size, 'bold'))
        t.penup()
        t.home()
        t.color('#F29407')
    
    
    # 饼身中间矩形条纹部分
    def body_center_line(width: "矩形宽度", height: "矩形高度"):
        t.penup()
        t.home()
        t.pensize(4)
        t.pendown()
        t.backward(width / 2)
        t.forward(width)
        t.left(90)
        t.forward(height)
        t.left(90)
        t.forward(width)
        t.left(90)
        t.forward(height * 2)
        t.left(90)
        t.forward(width)
        t.left(90)
        t.forward(height)
        t.penup()
        t.home()
    
    
    # 矩形条纹两侧的四个花纹 画笔轨迹是一样的 所以只需要传入不同的初始位置和角度即可复用代码
    def center_flower(start_point: "落笔位置", start_angle: "落笔朝向", angle_direction_change: "新朝向",
                    rectangle_height: "矩形高度", circle_direction: "花纹弧度"):
        t.penup()
        t.goto(start_point)
        t.pendown()
        t.setheading(start_angle)
        t.forward(10)
        t.setheading(angle_direction_change)
        t.forward(20)
        t.backward(rectangle_height * 2)
        t.forward(rectangle_height * 2)
        t.setheading(start_angle)
        t.circle(circle_direction * 70, 90)
        t.setheading(start_angle + 180)
        t.forward(60)
        t.setheading(angle_direction_change)
        t.forward(30)
        t.penup()
        t.home()
    
    
    # 饼身上下左右的花纹
    def out_flower(begin_x: "落笔横坐标", begin_y: "落笔纵坐标", start_angle: "落笔朝向"):
        t.penup()
        t.goto(begin_x, begin_y)
        t.pendown()
        t.setheading(start_angle)
        t.forward(20)
        t.right(90)
        t.circle(-100, 20)
    
        t.penup()
        t.goto(begin_x, begin_y)
        t.pendown()
        t.setheading(start_angle)
        t.right(90)
        t.circle(-100, 30)
        t.left(90)
        t.forward(45)
        t.left(95)
        t.circle(190, 50)
        t.left(95)
        t.forward(45)
        t.left(90)
        t.circle(-100, 31)
        t.setheading(start_angle)
        t.forward(20)
        t.left(90)
        t.circle(100, 20)
        t.penup()
        t.home()
    
        # 设置画布名称
    t.screen.title('月饼')
        # 画 饼身部分
    outfill_flower(18, '#F29407')
        # 画 饼身外围 花纹部分
    out_line_flower(18, '#FFDEAD')
        # 画内测的大圆 大圆的填充色比饼身略亮
    big_circle('#FFDEAD', '#F8B51D', 200)
        # 饼身中间矩形条纹部分
    body_center_line(12, 80)
        # 饼身上下左右的花纹
    out_flower(6, 110, 90)
    out_flower(-110, 6, 180)
    out_flower(-6, -110, 270)
    out_flower(110, -6, 360)
        # 可以再加点字
    text_content2 = {'中': (-50, 30), '秋': (50, 30), '乐': (50, -60), '快': (-50, -60)}  # 圆字坐标最后向下微调了一下
    write_font(text_content2, '#FCE6C9',40)
    
        # 隐藏画笔
    t.hideturtle()
        # 保持画布显示
    自制('YueBing!')
    turtle.done()

def 生成世界地图html():
    try:
        from pyecharts import options as opts
        from pyecharts.charts import Map
        from pyecharts.faker import Faker
        import webbrowser
    except:
        os.system('pip install pyecharts')
        time.sleep(2)
        from pyecharts import options as opts
        from pyecharts.charts import Map
        from pyecharts.faker import Faker
        import webbrowser

    c = (
    Map(init_opts=opts.InitOpts(width='1500px', height='1200px',bg_color='#E0EEEE'))
    # 加载世界地图实例
    .add("世界地图", [list(z) for z in zip(Faker.country, Faker.values())], "world")
    # 不显示地图标志
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
    # 配置项标题设置
    title_opts=opts.TitleOpts(title="世界地图示例"),
    visualmap_opts=opts.VisualMapOpts(max_=200)
    )
    # 生成超文本文件
    .render("世界地图.html")
    )
    print('生成成功！')
    webbrowser.open(Desktop + '/世界地图.html')

def 生成中国地图html():
    try:
        from pyecharts import options as opts
        from pyecharts.charts import Map3D
        from pyecharts.globals import ChartType
        import webbrowser
    except:
        os.system('pip install pyecharts')
        time.sleep(2)
        from pyecharts import options as opts
        from pyecharts.charts import Map3D
        from pyecharts.globals import ChartType
        import webbrowser

    c = (
    Map3D(init_opts=opts.InitOpts(width='1300px', height='1300px',bg_color='#EBEBEB'))
    .add_schema(
    itemstyle_opts=opts.ItemStyleOpts(
    color="#CDBA96",
    opacity=1,
    border_width=0.8,
    border_color="rgb(62,215,213)",
    ),
    map3d_label=opts.Map3DLabelOpts(
    is_show=True,
    text_style=opts.TextStyleOpts(
    color="#104E8B", font_size=16, background_color="rgba(0,0,0,0)"
    ),
    ),
    emphasis_label_opts=opts.LabelOpts(is_show=True),
    light_opts=opts.Map3DLightOpts(
    main_color="#FFEBCD",
    main_intensity=1.2,
    is_main_shadow=False,
    main_alpha=55,
    main_beta=10,
    ambient_intensity=0.3,
    ),
    )
    .add(series_name="", data_pair="", maptype=ChartType.MAP3D)
    # 全局设置地图属性
    .set_global_opts(
    title_opts=opts.TitleOpts(title="全国行政区划地图"),
    visualmap_opts=opts.VisualMapOpts(is_show=False),
    tooltip_opts=opts.TooltipOpts(is_show=True),
    )
    .render("中国3D地图.html")
    )
    webbrowser.open(Desktop + '/中国3D地图.html')

#有报错，弃用了
"""
def 生成3D地球html():
    try:
        import pyecharts.options as opts
        from pyecharts.charts import MapGlobe
        from pyecharts.faker import POPULATION

    except:
        os.system('pip install pyecharts')
        time.sleep(2)
        import pyecharts.options as opts
        from pyecharts.charts import MapGlobe
        from pyecharts.faker import POPULATION

    data = [x for _, x in POPULATION[1:]]
    low, high = min(data), max(data)
    c = (
    MapGlobe(init_opts=opts.InitOpts(width='1000px', height='1000px',bg_color='#FFFAFA',))
    .add_schema()
    .add(
    maptype="world",
    series_name="World Population",
    data_pair=POPULATION[1:],
    is_map_symbol_show=True,
    label_opts=opts.LabelOpts(is_show=True),
    )
    .set_global_opts(
    title_opts=opts.TitleOpts(title="3D 地球示例"),
    # 设置地球属性
    visualmap_opts=opts.VisualMapOpts(
    min_=low,
    max_=high,
    range_text=["max", "min"],
    is_calculable=True,
    range_color=["lightskyblue", "yellow", "orangered"],
    )
    )
    .render("3D地球.html")
    )
    print('生成成功！')
"""

class 数据库:
    clothes = ["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"]
    drinks = ["可乐", "雪碧", "橙汁", "绿茶", "奶茶", "百威", "青岛"]
    phones = ["小米", "三星", "华为", "苹果", "魅族", "VIVO", "OPPO"]
    fruits = ["草莓", "芒果", "葡萄", "雪梨", "西瓜", "柠檬", "车厘子"]
    animal = ["河马", "蟒蛇", "老虎", "大象", "兔子", "熊猫", "狮子"]
    cars = ["宝马", "法拉利", "奔驰", "奥迪", "大众", "丰田", "特斯拉"]
    dogs = ["哈士奇", "萨摩耶", "泰迪", "金毛", "牧羊犬", "吉娃娃", "柯基"]
    week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    week_en = "Saturday Friday Thursday Wednesday Tuesday Monday Sunday".split()
    clock = (
        "12a 1a 2a 3a 4a 5a 6a 7a 8a 9a 10a 11a 12p "
        "1p 2p 3p 4p 5p 6p 7p 8p 9p 10p 11p".split()
    )
    visual_color = [
        "#313695",
        "#4575b4",
        "#74add1",
        "#abd9e9",
        "#e0f3f8",
        "#ffffbf",
        "#fee090",
        "#fdae61",
        "#f46d43",
        "#d73027",
        "#a50026",
    ]
    months = ["{}月".format(i) for i in range(1, 13)]
    provinces = ["广东省", "北京市", "上海市", "江西省", "湖南省", "浙江省", "江苏省"]
    guangdong_city = ["汕头市", "汕尾市", "揭阳市", "阳江市", "肇庆市", "广州市", "惠州市"]
    country = [
        "China",
        "Canada",
        "Brazil",
        "Russia",
        "United States",
        "Africa",
        "Germany",
    ]

    def choose(self) -> list:
        return random.choice(
            [
                self.clothes,
                self.drinks,
                self.phones,
                self.fruits,
                self.animal,
                self.dogs,
                self.week,
            ]
        )

    @staticmethod
    def rand_color() -> str:
        return random.choice(
            [
                "#c23531",
                "#2f4554",
                "#61a0a8",
                "#d48265",
                "#749f83",
                "#ca8622",
                "#bda29a",
                "#6e7074",
                "#546570",
                "#c4ccd3",
                "#f05b72",
                "#444693",
                "#726930",
                "#b2d235",
                "#6d8346",
                "#ac6767",
                "#1d953f",
                "#6950a1",
            ]
        )

    @staticmethod
    def img_path(path: str, prefix: str = "images") -> str:
        return os.path.join(prefix, path)

    economize = [
        '河北',
        '山西',
        '黑龙江',
        '吉林',
        '辽宁',
        '江苏',
        '浙江',
        '安徽',
        '福建',
        '江西',
        '山东',
        '河南',
        '湖北',
        '湖南',
        '广东',
        '海南',
        '四川',
        '贵州',
        '云南',
        '陕西',
        '甘肃',
        '青海',
        '台湾',
        #自治区
        '内蒙古自治区',
        '广西壮族自治区',
        '宁夏回族自治区',
        '新疆维吾尔自治区',
        '西藏自治区',
        #直辖市
        '北京市',
        '上海市',
        '天津市',
        '重庆市',
        #特别行政区
        '香港特别行政区',
        '澳门特别行政区'
    ]

def 获取管理员权限():
    #导入模块
    import ctypes
    import sys

    print('正在获取管理员权限...')
    # 判断是否有administrator（管理员）权限
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    #如果没有administrator（管理员）权限那就用administrator（管理员）权限重新打开程序.
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        print('已成功获取管理员权限！')
        sys.exit()

def 打开(title,file,limitation):
    global open

    from tkinter import filedialog

    open=filedialog.askopenfilename(title=title, filetypes=[(file,limitation),])

def 下载(url, destination,Savelocation):
        try:
            os.chdir(Savelocation)
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持活动连接的空chunk
                        file.write(chunk)

            print(f"Downloaded successfully to {destination}")
        except Exception as e:
            print(f"Failed to download the file due to error: {e}")

def DrawPrint画打印():
    自制('DrawPrint.')
    自制('Hi!')
    自制('My name is HuangYiYi.')
    自制('end.')

def 摇起来():
    """大惊喜!"""
    try:
        import requests
        import pygame
    except:
        print('Time...')
        os.system('pip install requests')
        os.system('pip install pygame')
        time.sleep(5)
        import requests
        import pygame

    下载(url='http://er.sycdn.kuwo.cn/e838e7ffcf119dee6da3e96d26fe6b47/67826379/resource/30106/trackmedia/M8000022eEIQ12m218.mp3',destination='music.mp3',Savelocation="D:/")
    自制('music!')
    print('摇起来!')
    os.chdir(Desktop)
    time.sleep(0.5)
    file_path = r'D:/music.mp3'
    pygame.mixer.init()

    pygame.mixer.music.load(r'D:/music.mp3')
    pygame.mixer.music.play()


    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    自制('hhh')

def 原神启动():
    try:
        import webbrowser
        import pyautogui as pg
    except:
        os.system('pip install pyautogui')
        time.sleep(2.5)
        import webbrowser
        import pyautogui as pg

    webbrowser.open('https://yunchenqwq.github.io/Genshin_Start.github.io/')
    for i in range(5):
        time.sleep(0.1)
        pg.click(300,600)

from turtle import *
def 哆啦A梦():
    # 无轨迹跳跃
    def my_goto(x, y):
        penup()
        goto(x, y)
        pendown()

    # 眼睛
    def eyes():
        fillcolor("#ffffff")
        begin_fill()

        tracer(False)
        a = 2.5
        for i in range(120):
            if 0 <= i < 30 or 60 <= i < 90:
                a -= 0.05
                lt(3)
                fd(a)
            else:
                a += 0.05
                lt(3)
                fd(a)
        tracer(True)
        end_fill()


    # 胡须
    def beard():
        my_goto(-32, 135)
        seth(165)
        fd(60)

        my_goto(-32, 125)
        seth(180)
        fd(60)

        my_goto(-32, 115)
        seth(193)
        fd(60)

        my_goto(37, 135)
        seth(15)
        fd(60)

        my_goto(37, 125)
        seth(0)
        fd(60)

        my_goto(37, 115)
        seth(-13)
        fd(60)

    # 嘴巴
    def mouth():
        my_goto(5, 148)
        seth(270)
        fd(100)
        seth(0)
        circle(120, 50)
        seth(230)
        circle(-120, 100)

    # 围巾
    def scarf():
        fillcolor('#e70010')
        begin_fill()
        seth(0)
        fd(200)
        circle(-5, 90)
        fd(10)
        circle(-5, 90)
        fd(207)
        circle(-5, 90)
        fd(10)
        circle(-5, 90)
        end_fill()

    # 鼻子
    def nose():
        my_goto(-10, 158)
        seth(315)
        fillcolor('#e70010')
        begin_fill()
        circle(20)
        end_fill()

    # 黑眼睛
    def black_eyes():
        seth(0)
        my_goto(-20, 195)
        fillcolor('#000000')
        begin_fill()
        circle(13)
        end_fill()

        pensize(6)
        my_goto(20, 205)
        seth(75)
        circle(-10, 150)
        pensize(3)

        my_goto(-17, 200)
        seth(0)
        fillcolor('#ffffff')
        begin_fill()
        circle(5)
        end_fill()
        my_goto(0, 0)



    # 脸
    def face():

        fd(183)
        lt(45)
        fillcolor('#ffffff')
        begin_fill()
        circle(120, 100)
        seth(180)
        # print(pos())
        fd(121)
        pendown()
        seth(215)
        circle(120, 100)
        end_fill()
        my_goto(63.56,218.24)
        seth(90)
        eyes()
        seth(180)
        penup()
        fd(60)
        pendown()
        seth(90)
        eyes()
        penup()
        seth(180)
        fd(64)

    # 头型
    def head():
        penup()
        circle(150, 40)
        pendown()
        fillcolor('#00a0de')
        begin_fill()
        circle(150, 280)
        end_fill()

    # 画哆啦A梦
    def Doraemon():
        # 头部
        head()

        # 围脖
        scarf()

        # 脸
        face()

        # 红鼻子
        nose()

        # 嘴巴
        mouth()

        # 胡须
        beard()

        # 身体
        my_goto(0, 0)
        seth(0)
        penup()
        circle(150, 50)
        pendown()
        seth(30)
        fd(40)
        seth(70)
        circle(-30, 270)


        fillcolor('#00a0de')
        begin_fill()

        seth(230)
        fd(80)
        seth(90)
        circle(1000, 1)
        seth(-89)
        circle(-1000, 10)

        # print(pos())

        seth(180)
        fd(70)
        seth(90)
        circle(30, 180)
        seth(180)
        fd(70)

        # print(pos())
        seth(100)
        circle(-1000, 9)

        seth(-86)
        circle(1000, 2)
        seth(230)
        fd(40)

        # print(pos())


        circle(-30, 230)
        seth(45)
        fd(81)
        seth(0)
        fd(203)
        circle(5, 90)
        fd(10)
        circle(5, 90)
        fd(7)
        seth(40)
        circle(150, 10)
        seth(30)
        fd(40)
        end_fill()

        # 左手
        seth(70)
        fillcolor('#ffffff')
        begin_fill()
        circle(-30)
        end_fill()

        # 脚
        my_goto(103.74, -182.59)
        seth(0)
        fillcolor('#ffffff')
        begin_fill()
        fd(15)
        circle(-15, 180)
        fd(90)
        circle(-15, 180)
        fd(10)
        end_fill()

        my_goto(-96.26, -182.59)
        seth(180)
        fillcolor('#ffffff')
        begin_fill()
        fd(15)
        circle(15, 180)
        fd(90)
        circle(15, 180)
        fd(10)
        end_fill()

        # 右手
        my_goto(-133.97, -91.81)
        seth(50)
        fillcolor('#ffffff')
        begin_fill()
        circle(30)
        end_fill()

        # 口袋
        my_goto(-103.42, 15.09)
        seth(0)
        fd(38)
        seth(230)
        begin_fill()
        circle(90, 260)
        end_fill()

        my_goto(5, -40)
        seth(0)
        fd(70)
        seth(-90)
        circle(-70, 180)
        seth(0)
        fd(70)

        #铃铛
        my_goto(-103.42, 15.09)
        fd(90)
        seth(70)
        fillcolor('#ffd200')
        # print(pos())
        begin_fill()
        circle(-20)
        end_fill()
        seth(170)
        fillcolor('#ffd200')
        begin_fill()
        circle(-2, 180)
        seth(10)
        circle(-100, 22)
        circle(-2, 180)
        seth(180-10)
        circle(100, 22)
        end_fill()
        goto(-13.42, 15.09)
        seth(250)
        circle(20, 110)
        seth(90)
        fd(15)
        dot(10)
        my_goto(0, -150)

        # 画眼睛
        black_eyes()

    title('哆 啦 A 梦')
    screensize(800,600, "#f0f0f0")
    pensize(3)  # 画笔宽度
    speed(9)    # 画笔速度
    Doraemon()
    my_goto(100, -300)
    write('哆 啦 A 梦', font=("Bradley Hand ITC", 30, "bold"))
    mainloop()

from math import sin, cos, pi, log
from tkinter import *
import random

def 动态爱心(title,text):
    """动态爱心"""
    CANVAS_WIDTH = 640  # 画布的宽
    CANVAS_HEIGHT = 640  # 画布的高
    CANVAS_CENTER_X = CANVAS_WIDTH / 2  # 画布中心的X轴坐标
    CANVAS_CENTER_Y = CANVAS_HEIGHT / 2  # 画布中心的Y轴坐标
    IMAGE_ENLARGE = 11  # 放大比例
    HEART_COLOR = "#e77c8e"  # 心的颜色#ff7171


    def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
        """
        “爱心函数生成器”
        :param shrink_ratio: 放大比例
        :param t: 参数
        :return: 坐标
        """
        # 基础函数
        x = 16 * (sin(t) ** 3)
        y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

        # 放大
        x *= shrink_ratio
        y *= shrink_ratio

        # 移到画布中央
        x += CANVAS_CENTER_X
        y += CANVAS_CENTER_Y

        return int(x), int(y)


    def scatter_inside(x, y, beta=0.15):
        """
        随机内部扩散
        :param x: 原x
        :param y: 原y
        :param beta: 强度
        :return: 新坐标
        """
        ratio_x = - beta * log(random.random())
        ratio_y = - beta * log(random.random())

        dx = ratio_x * (x - CANVAS_CENTER_X)
        dy = ratio_y * (y - CANVAS_CENTER_Y)

        return x - dx, y - dy


    def shrink(x, y, ratio):
        """
        抖动
        :param x: 原x
        :param y: 原y
        :param ratio: 比例
        :return: 新坐标
        """
        force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
        dx = ratio * force * (x - CANVAS_CENTER_X)
        dy = ratio * force * (y - CANVAS_CENTER_Y)
        return x - dx, y - dy


    def curve(p):
        """
        自定义曲线函数，调整跳动周期
        :param p: 参数
        :return: 正弦
        """
        # 可以尝试换其他的动态函数，达到更有力量的效果（贝塞尔？）
        return 2 * (3 * sin(4 * p)) / (2 * pi)


    class Heart:
        """
        爱心类
        """

        def __init__(self, generate_frame=20):
            self._points = set()  # 原始爱心坐标集合
            self._edge_diffusion_points = set()  # 边缘扩散效果点坐标集合
            self._center_diffusion_points = set()  # 中心扩散效果点坐标集合
            self.all_points = {}  # 每帧动态点坐标
            self.build(2000)

            self.random_halo = 1000

            self.generate_frame = generate_frame
            for frame in range(generate_frame):
                self.calc(frame)

        def build(self, number):
            # 爱心
            for _ in range(number):
                t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
                x, y = heart_function(t)
                self._points.add((x, y))

            # 爱心内扩散
            for _x, _y in list(self._points):
                for _ in range(3):
                    x, y = scatter_inside(_x, _y, 0.05)
                    self._edge_diffusion_points.add((x, y))

            # 爱心内再次扩散
            point_list = list(self._points)
            for _ in range(4000):
                x, y = random.choice(point_list)
                x, y = scatter_inside(x, y, 0.17)
                self._center_diffusion_points.add((x, y))

        @staticmethod
        def calc_position(x, y, ratio):
            # 调整缩放比例
            force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)  # 魔法参数

            dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
            dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

            return x - dx, y - dy

        def calc(self, generate_frame):
            ratio = 10 * curve(generate_frame / 10 * pi)  # 圆滑的周期的缩放比例

            halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
            halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

            all_points = []

            # 光环
            heart_halo_point = set()  # 光环的点坐标集合
            for _ in range(halo_number):
                t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
                x, y = heart_function(t, shrink_ratio=11.6)  # 魔法参数
                x, y = shrink(x, y, halo_radius)
                if (x, y) not in heart_halo_point:
                    # 处理新的点
                    heart_halo_point.add((x, y))
                    x += random.randint(-14, 14)
                    y += random.randint(-14, 14)
                    size = random.choice((1, 2, 2))
                    all_points.append((x, y, size))

            # 轮廓
            for x, y in self._points:
                x, y = self.calc_position(x, y, ratio)
                size = random.randint(1, 3)
                all_points.append((x, y, size))

            # 内容
            for x, y in self._edge_diffusion_points:
                x, y = self.calc_position(x, y, ratio)
                size = random.randint(1, 2)
                all_points.append((x, y, size))

            for x, y in self._center_diffusion_points:
                x, y = self.calc_position(x, y, ratio)
                size = random.randint(1, 2)
                all_points.append((x, y, size))

            self.all_points[generate_frame] = all_points

        def render(self, render_canvas, render_frame):
            for x, y, size in self.all_points[render_frame % self.generate_frame]:
                render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


    def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
        render_canvas.delete('all')
        render_heart.render(render_canvas, render_frame)
        render_canvas.create_text(320, 320, text=text, fill='#e77c8e', font=('微软雅黑', 15, 'bold'))  # 此处可自定义
        main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)



    if __name__ == '__main__':
        root = Tk()  # 一个Tk
        root.title(title)  # 此处可自定义
        canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
        canvas.pack()
        heart = Heart()  # 心
        draw(root, canvas, heart)  # 开始画
        root.mainloop()


def 中国数据可视化(select):
        """各省人口数据可视化"""
        if select == 1:
            try:
                from pyecharts import options as opts
                from pyecharts.charts import Map
            except:
                os.system('pip install pyecharts')
                time.sleep(2)
                from pyecharts import options as opts
                from pyecharts.charts import Map

            # 2019全国各省人口数量排名，单位：万，展示前十

            province_population = [
                ["广东省", 11169],
                ["山东省", 10005.83],
                ["河南省", 9559.13],
                ["四川省", 8302],
                ["江苏省", 8029.3],
                ["河北省", 7519.52],
                ["湖南省", 6860.2],
                ["安徽省", 6254.8],
                ["湖北省", 5902],
                ["浙江省", 5657]
            ]

            province_population
            map = (
                Map()
                .add("各省人口数量",province_population,"china")
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="2019全国各省人口数量排名"),
                    visualmap_opts=opts.VisualMapOpts(max_=12000)
                )
            )
            from IPython.display import HTML

            # 同上，读取 HTML 文件内容
            # bar.render()的值是一个路径，以字符串形式表示
            with open(map.render(), 'r', encoding='utf-8') as file:
                html_content = file.read()

            # 直接在 JupyterLab 中渲染 HTML
            HTML(html_content)

        """北京各区人口数量"""
        if select == 2:
            # 2019年北京各区人口数量，前七个
            beijing = [
                ["朝阳区",395.5],
                ["海淀区",369.4],
                ["丰台区",232.4],
                ["昌平区",196.3],
                ["大兴区",156.2],
                ["通州区",137.8],
                ["西城区",129.8]
            ]
            map = (
                Map()
                .add("各区人口",beijing, "北京")
                .set_global_opts(
                        title_opts=opts.TitleOpts(title="2019年北京各区人口数量"),
                        visualmap_opts=opts.VisualMapOpts(max_=400)
                )
            )
            from IPython.display import HTML

            # 同上，读取 HTML 文件内容
            # bar.render()的值是一个路径，以字符串形式表示
            with open(map.render(), 'r', encoding='utf-8') as file:
                html_content = file.read()

            # 直接在 JupyterLab 中渲染 HTML
            HTML(html_content)

def 中国地图():
        try:
            from pyecharts import options as opts
            from pyecharts.charts import Map
            import webbrowser
        except:
            os.system('pip install pyecharts')
            time.sleep(2.5)
            from pyecharts import options as opts
            from pyecharts.charts import Map
            import webbrowser

        province_dis = {'宁夏':55,'河南': 145, '北京': 137, '河北': 121, '辽宁': 112, '江西': 16, '上海':120, '安徽': 110, '江苏': 116, '湖南': 119,'浙江': 113, '海南': 12, '广东': 212, '湖北': 18, '黑龙江': 111, '澳门': 11, '陕西': 111, '四川': 17, '内蒙古': 13, '重庆': 13,'广西':81,'云南': 16, '贵州': 21, '吉林': 31, '山西': 11, '山东': 111, '福建': 41, '青海': 51, '天津': 11,'新疆':150,'西藏':170,'甘肃':120,'台湾':31}

        provice = list(province_dis.keys())
        values = list(province_dis.values())

        china = (
            Map()
            .add("", [list(z) for z in zip(provice, values)], "china")
            .set_global_opts(title_opts=opts.TitleOpts(title="中国地图"), visualmap_opts=opts.VisualMapOpts())
        )

        # 打开html
        china.render("中国地图.html")
        webbrowser.open(Desktop+'/中国地图.html')

def 世界地图(title1,title2):
    try:
        from pyecharts import options as opts
        from pyecharts.charts import Map
        import random
        import webbrowser
    except:
        os.system('pip install pyecharts')
        time.sleep(2.5)
        from pyecharts import options as opts
        from pyecharts.charts import Map
        import random
        import webbrowser

    ultraman = [
    ['Russia', 0],
    ['China', 0],
    ['United States', 0],
    ['Australia', 0]
    ]

    monster = [
    ['India', 0],
    ['Canada', 0],
    ['France', 0],
    ['Brazil', 0]
    ]

    def data_filling(array):
        ''' 
        作用：给数组数据填充随机数
        '''
        for i in array:
            # 随机生成1到1000的随机数
            i[1] = random.randint(1,1000)
            print(i)
            
    data_filling(ultraman)
    data_filling(monster)

    def create_world_map():
        ''' 
        作用：生成世界地图
        '''
        (   # 大小设置
            Map()
            .add(
                series_name=title1, 
                data_pair=ultraman, 
                maptype="world", 
            )
            .add(
                series_name=title2, 
                data_pair=monster, 
                maptype="world", 
            )
            # 全局配置项
            .set_global_opts(
                # 设置标题
                title_opts=opts.TitleOpts(title="世界地图"),
                # 设置标准显示
                visualmap_opts=opts.VisualMapOpts(max_=1000, is_piecewise=False),
            )
            # 系列配置项
            .set_series_opts(
                # 标签名称显示，默认为True
                label_opts=opts.LabelOpts(is_show=False, color="blue")
            )
            # 生成本地html文件
            .render("世界地图.html")
        )

    create_world_map()
    webbrowser.open(Desktop+'/世界地图.html')

def 河北地图(title1,title2):
    try:
        from pyecharts import options as opts
        from pyecharts.charts import Map
        import random
        import webbrowser
    except:
        os.system('pip install pyecharts')
        time.sleep(2.5)
        from pyecharts import options as opts
        from pyecharts.charts import Map
        import random
        import webbrowser

    ultraman = [
    ['承德市', 0],
    ['邯郸市', 0],
    ['石家庄市', 0]
    ]

    monster = [
    ['张家口市', 0],
    ['秦皇岛市', 0],
    ['保定市', 0]
    ]

    def data_filling(array):
        ''' 
        作用：给数组数据填充随机数
        '''
        for i in array:
            # 随机生成1到1000的随机数
            i[1] = random.randint(1,1000)
            print(i)
            
    data_filling(ultraman)
    data_filling(monster)

    def create_province_map():
        ''' 
        作用：生成省份地图
        '''
        (   # 大小设置
            Map()
            .add(
                series_name=title1, 
                data_pair=ultraman, 
                maptype="河北", 
            )
            .add(
                series_name=title2, 
                data_pair=monster, 
                maptype="河北", 
            )
            # 全局配置项
            .set_global_opts(
                # 设置标题
                title_opts=opts.TitleOpts(title="省份地图"),
                # 设置标准显示
                visualmap_opts=opts.VisualMapOpts(max_=1000, is_piecewise=False),
            )
            # 系列配置项
            .set_series_opts(
                # 标签名称显示，默认为True
                label_opts=opts.LabelOpts(is_show=True, color="blue")
            )
            # 生成本地html文件
            .render("省份地图.html")
        )

    create_province_map()
    webbrowser.open(Desktop+'/中国地图.html')

if __name__ == '__main__':
    """大惊喜!"""
    try:
        import requests
        import pygame
    except:
        print('Time...')
        os.system('pip install requests')
        os.system('pip install pygame')
        time.sleep(5)
        import requests
        import pygame

    下载(url='http://er.sycdn.kuwo.cn/e838e7ffcf119dee6da3e96d26fe6b47/67826379/resource/30106/trackmedia/M8000022eEIQ12m218.mp3',destination='music.mp3',Savelocation="D:/")
    自制('music!')
    print('摇起来!')
    os.chdir(Desktop)
    time.sleep(0.5)
    file_path = r'D:/music.mp3'
    pygame.mixer.init()

    pygame.mixer.music.load(r'D:/music.mp3')
    pygame.mixer.music.play()


    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    自制('hhh')

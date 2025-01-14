art = """
                      /^--^\     /^--^\     /^--^\
                      \____/     \____/     \____/
                     /      \   /      \   /      \
KAT                 |        | |        | |        |
                     \__  __/   \__  __/   \__  __/
|^|^|^|^|^|^|^|^|^|^|^|^\ \^|^|^|^/ /^|^|^|^|^\ \^|^|^|^|^|^|^|^|^|^|^|^|
| | | | | | | | | | | | |\ \| | |/ /| | | | | | \ \ | | | | | | | | | | |
########################/ /######\ \###########/ /#######################
| | | | | | | | | | | | \/| | | | \/| | | | | |\/ | | | | | | | | | | | |
|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|

"""

def hi():
    print(art)

def random_pic():
    import random
    from check_os_ver.hi import hi as hi1
    from jacob_os_version_check.hi import hi as hi2
    funs = [hi1, hi2]
    rf = random.choice(funs)
    rf()
    print("random_pic".center(123, "*"));

def random_game():
    import random
    import check_os_ver.hi as p1
    import jacob_os_version_check.hi as p2
    packages = [p1, p2]
    p = random.choice(packages)
    p.hi()
    print("random_game".center(123, "*"));

def random_match():
    import random
    rnum = random.randint(1, 8)

    match rnum:
        case 1:
            from check_os_ver.hi import hi
            hi()
        case 2:
            from hj_check_os_version import hi
            hi()
        case 3:
            from jacob_os_version_check.hi import hi
            hi()
        case 4:
            from lucas_check_os_ver.hi import hi
            hi()
        case 5:
            from stundrg_check_os_ver.hi import hi
            hi()
        case 6:
            from cho_check_os_ver.hi import hi
            hi()
        case 7:
            from nunininu_check_os_ver.hi import hi
            hi()
        case 8:
            from seo_check_os_version.hi import hi
            hi()
        case _:
            print("오류");
    print("random_game".center(123, "*"));
    
#import random
#from check_os_ver.hi import hi as hi1
#from hj_check_os_version.hi import hi as hi2
#from jacob_os_version_check.hi import hi as hi3
#from lucas_check_os_ver.hi import hi as hi4
#from stundrg_check_os_ver.hi import hi as hi5
#from nunininu_check_os_ver.hi import hi as hi6


#a = random.randint(1, 8)

#if a==1:
    #A=hi1()
#elif a==2:
    #A=hi2()
#elif a==3:
    #A=hi3()
#elif a==4:
    #A=hi4()
#elif a==5:
    #A=hi5()
#elif a==6:
    #A=hi6()
#elif a==7:
    #A=hi7()

#print(A)

#def random_pic():
#import random

#rnum = rando.ranint(1, 8)

    #match rnum:
       # case 1:
           # from check_os_ver.hi import hi
            #hi()
        #case 2:
            #from hj-check-os-version==0.2.1 import hi
            #hi()
        #case 3:
            #from jacob-os-version-check==0.2.4 import hi
    #from lucas-check-os-ver==0.2.0 import hi
    #from stundrg-check-os-ver==0.2.3 import hi
    #from cho-check-os-ver/0.2.3/ import hi
    #from nunininu-check-os-ver/ import hi

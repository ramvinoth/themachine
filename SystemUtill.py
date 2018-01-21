def set_password_admin(username, password):
    from win32com import adsi
    ads_obj = adsi.ADsGetObject("WinNT://localhost/%s,user" % username)
    ads_obj.Getinfo()
    ads_obj.SetPassword(password)

def set_password_user(username, password, oldpass):
    import win32net
    win32net.NetUserChangePassword("WinNT://localhost/",username,oldpass,password)

def verify_success(username, password):
    from win32security import LogonUser
    from win32con import LOGON32_LOGON_INTERACTIVE, LOGON32_PROVIDER_DEFAULT
    try:
        LogonUser(username, None, password, LOGON32_LOGON_INTERACTIVE, LOGON32_PROVIDER_DEFAULT)
    except:
        return False
    return True

u = "VINZ"
p = "vinz143"
#set_password_admin(u, p)
set_password_user(u, p, "hackerz143")
if verify_success(u, p):
    print "W00t it workz"
else:
    print "Continue Googling"
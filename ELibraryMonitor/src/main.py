#coding:GBK
import time
import os
import psutil
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
import base64
import smtplib
import socket

def send_mail(send_from, send_to, subject, message, emailfiles=[], server="localhost", user=None, password=None):
    try:
        if emailfiles != None:
            files = emailfiles.split(";")
        else:
            files = []
        assert type(send_to) == list
        assert type(files) == list
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(message))
        for mfile in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(mfile, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(mfile))
            msg.attach(part)
        smtp = smtplib.SMTP(server)
        if (user != None):
            smtp.ehlo()
            smtp_userid64 = base64.encodestring(user)
            smtp.docmd("auth", "login " + smtp_userid64[:-1])
        if password != None:
            smtp_pass64 = base64.encodestring(password)
            smtp.docmd(smtp_pass64[:-1])
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()#coding:gbk
        return True
    except Exception, e:
        einfo = "EmailError:" + str(e)
        print einfo
        return False

def getCPUstate(interval=1):
    #cpu = psutil.cpu_percent(interval)
    cputime = psutil.cpu_times_percent()
    cpu = cputime.user + cputime.system
    if cpu >= 70:
        result = False
    else:
        result = True
    return result, "[CPU:%s%%]    User:%s%%    System:%s%%    Idle:%s%%" % (int(cpu), int(cputime.user), int(cputime.system), int(cputime.idle))

def getMemorystate():
    phymem = psutil.phymem_usage()
    buffers = getattr(psutil, 'phymem_buffers', lambda: 0)()
    cached = getattr(psutil, 'cached_phymem', lambda: 0)()
    used = phymem.total - (phymem.free + buffers + cached)
    free = phymem.free + buffers + cached
    line = "[Memory:%s%%]    Used:%s   Idle:%s" % (
        phymem.percent,
        str(int(used / 1024 / 1024)) + "M",
        str(int(free / 1024 / 1024)) + "M"
    )
    if (free / 1024 / 1024) < 500 :
        result = False
    else:
        result = True
    return result, line

def WriteLog(msg):
    logpath = os.path.dirname(__file__)
    log = open(os.path.join(logpath,"monitor_log.txt"), "a+")
    log.write(msg)
    log.write("\n")
    log.close()

if __name__ == '__main__':
    temp = 0
    while True:
        try:
            edict = {"HTSERVER1":"103.15.28.223","HTSERVER2":"103.15.28.224","HTSERVER3":"103.15.28.225"}
            dataTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            hostname = socket.gethostname() 
            cpuIsFine, cpumsg = getCPUstate()
            memoryIsFine, memorymsg = getMemorystate()
            emailmsg = """
    %s
        *%s  
        *%s    
                """ % (dataTime, cpumsg, memorymsg)
            print emailmsg
            if not cpuIsFine:
                temp += 1
            else:
                temp = 0
            print '=',temp,'='
            if (not memoryIsFine) or temp>=3:
                temp = 0
                emailtitle = u"【警告】设备[%s]的系统资源不足，请检查设备运行状况！" % edict.get(hostname,hostname)
                result = send_mail('alvin.yao@campray.com', #发信人
                                  #['alvin.yao@campray.com'], #收件人
                                  ['monica.xiao@campray.com','cody.li@campray.com','andy.lin@campray.com','phills.li@campray.com','alvin.yao@campray.com'], #收件人
                                  emailtitle, #标题
                                  emailmsg, #内容
                                  None, #附件
                                  'smtp.exmail.qq.com', #邮件服务器
                                  'alvin.yao@campray.com', #用户名
                                  'lyyao105')#密码
                if result:
                    emailmsg += "Send Email [Succeed]!"
                    print "Send Email [Succeed]!"
                else:
                    emailmsg += "Send Email [Failed]!"
                    print "Send Email [Failed]!"
                #print emailmsg
                WriteLog(emailmsg)
            print "=-" * 10
        except Exception,e:
            print str(e)
            WriteLog(str(e))
        finally:
            time.sleep(30)

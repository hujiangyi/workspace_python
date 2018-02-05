import jpype

def start():
    import os
    homedir = os.environ['pythonpath']
    print 'homedir:',homedir
    jvmPath = jpype.getDefaultJVMPath()
    print 'jvmPath:',jvmPath
    libdir = homedir + "\\common\\SnmpAts\\lib\\"

    astjar = libdir + "ast.jar"
    commonsloggingjar = libdir + "commons-logging-1.1.1.jar"
    dom4jjar = libdir + "dom4j-1.6.1.jar"
    jxljar = libdir + "jxl.jar"
    log4joverslf4jjar = libdir + "log4j-over-slf4j-1.7.6.jar"
    logbackclassicjar = libdir + "logback-classic-1.1.1.jar"
    logbackcorejar = libdir + "logback-core-1.1.1.jar"
    mibblemibsjar = libdir + "mibble-mibs-2.9.3.jar"
    mibbleparserjar = libdir + "mibble-parser-2.9.3.jar"
    poijar = libdir + "poi-3.9-20121203.jar"
    poiexcelantjar = libdir + "poi-excelant-3.9-20121203.jar"
    poiooxmljar = libdir + "poi-ooxml-3.9-20121203.jar"
    poiooxmlschemasjar = libdir + "poi-ooxml-schemas-3.9-20121203.jar"
    poiscratchpadjar = libdir + "poi-scratchpad-3.9-20121203.jar"
    quartzjar = libdir + "quartz-2.1.7.jar"
    slf4japijar = libdir + "slf4j-api-1.7.6.jar"
    snmp4jjar = libdir + "snmp4j-2.2.1.jar"
    xmlbeansjar = libdir + "xmlbeans-2.3.0.jar"
    classpath = astjar + ";" + commonsloggingjar + ";" + dom4jjar + ";" + jxljar + ";" + log4joverslf4jjar + ";" + logbackclassicjar + ";" + logbackcorejar + ";" + mibblemibsjar+ ";" + mibbleparserjar + ";" + poijar + ";" + poiexcelantjar + ";" + poiooxmljar + ";" + poiooxmlschemasjar + ";" + poiscratchpadjar + ";" + quartzjar + ";" + slf4japijar+ ";" + snmp4jjar + ";" + xmlbeansjar
    #print 'classpath:',classpath
#    jvmArg = "-Djava.class.path=" + classpath 
    jvmArg = ["-Djava.class.path=" + classpath,"-Xms128M -Xmx512M -XX:PermSize=64M -XX:MaxPermSize=128M"]
    jpype.startJVM(jvmPath,jvmArg)   
    PythonInterface = jpype.JClass("com.topvision.ast.python.PythonInterface")
    pythonInterface = PythonInterface()
    return pythonInterface

def shutdown():
    jpype.shutdownJVM()    
    return
        


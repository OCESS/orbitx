        ON ERROR GOTO 2000
        CLS
        DEFDBL T
        DIM zp$(11)
        OPEN "R", #5, "backup.RND", 4364
        inpSTR$=space$(4364)
        get #5, 1, inpSTR$
        if len(inpSTR$)<>4364 then knt=0:goto 5
        knt = cvl(mid$(inpSTR$,10,4))
        ERRflag=2
       
       
5       OPEN "R", #1, "sevpath.RND", 25
        inpSTR$=space$(25)
        FOR i = 1 TO 11
         GET #1, i, inpSTR$
         FOR j = 1 TO 25
          zz$ = MID$(inpSTR$, j, 1)
          IF zz$ = " " THEN zp$(i) = LEFT$(inpSTR$, j - 1): goto 6
         NEXT j
6       NEXT i
       
        LOCATE 1, 1, 0
        COLOR 11, 0: PRINT "ORBIT/EECOM File Server System";
        LOCATE 2, 1
11      COLOR 10, 0: PRINT "a"; : COLOR 9, 0: LOCATE 2, 3: PRINT "Flight:    ["; zp$(1); "]"; : COLOR 11, 0: INPUT "", Zpath1$
        IF Zpath1$ = "" THEN Zpath1$ = zp$(1)
        if len(Zpath1$)>24 then locate 2,1:print space$(79);:locate 2,1:goto 11
12      COLOR 10, 0: PRINT "b"; : COLOR 9, 0: LOCATE 3, 3: PRINT "Mirror:    ["; zp$(2); "]"; : COLOR 11, 0: INPUT "", Zpath2$
        IF Zpath2$ = "" THEN Zpath2$ = zp$(2)
        if len(Zpath2$)>24 then locate 3,1:print space$(79);:locate 3,1:goto 12
13      COLOR 10, 0: PRINT "c"; : COLOR 9, 0: LOCATE 4, 3: PRINT "Telemetry: ["; zp$(3); "]"; : COLOR 11, 0: INPUT "", Zpath3$
        IF Zpath3$ = "" THEN Zpath3$ = zp$(3)
        if len(Zpath3$)>24 then locate 4,1:print space$(79);:locate 4,1:goto 13
14      COLOR 10, 0: PRINT "d"; : COLOR 9, 0: LOCATE 5, 3: PRINT "Simulator: ["; zp$(4); "]"; : COLOR 11, 0: INPUT "", Zpath4$
        IF Zpath4$ = "" THEN Zpath4$ = zp$(4)
        if len(Zpath4$)>24 then locate 5,1:print space$(79);:locate 5,1:goto 14
15      COLOR 10, 0: PRINT "e"; : COLOR 9, 0: LOCATE 6, 3: PRINT "Display:   ["; zp$(8); "]"; : COLOR 11, 0: INPUT "", Zpath8$
        IF Zpath8$ = "" THEN Zpath8$ = zp$(8)
        if len(Zpath5$)>24 then locate 6,1:print space$(79);:locate 6,1:goto 15
16      COLOR 10, 0: PRINT "f"; : COLOR 9, 0: LOCATE 7, 3: PRINT "Hab EECOM: ["; zp$(5); "]"; : COLOR 11, 0: INPUT "", Zpath5$
        IF Zpath5$ = "" THEN Zpath5$ = zp$(5)
        if len(Zpath6$)>24 then locate 7,1:print space$(79);:locate 7,1:goto 16
17      COLOR 10, 0: PRINT "g"; : COLOR 9, 0: LOCATE 8, 3: PRINT "MC EECOM:  ["; zp$(6); "]"; : COLOR 11, 0: INPUT "", Zpath6$
        IF Zpath6$ = "" THEN Zpath6$ = zp$(6)
        if len(Zpath7$)>24 then locate 8,1:print space$(79);:locate 8,1:goto 17
18      COLOR 10, 0: PRINT "h"; : COLOR 9, 0: LOCATE 9, 3: PRINT "SIM EECOM: ["; zp$(7); "]"; : COLOR 11, 0: INPUT "", Zpath7$
        IF Zpath7$ = "" THEN Zpath7$ = zp$(7)
        if len(Zpath8$)>24 then locate 9,1:print space$(79);:locate 9,1:goto 18
19      COLOR 10, 0: PRINT "i"; : COLOR 9, 0: LOCATE 10, 3: PRINT "Hab Eng:   ["; zp$(9); "]"; : COLOR 11, 0: INPUT "", Zpath9$
        IF Zpath9$ = "" THEN Zpath9$ = zp$(9)
        if len(Zpath9$)>24 then locate 10,1:print space$(79);:locate 10,1:goto 19
20      COLOR 10, 0: PRINT " "; : COLOR 9, 0: LOCATE 11, 3: PRINT "Sim Mirror:["; zp$(10); "]"; : COLOR 11, 0: INPUT "", Zpath10$
        IF Zpath10$ = "" THEN Zpath10$ = zp$(10)
        if len(Zpath10$)>24 then locate 11,1:print space$(79);:locate 11,1:goto 20
21      COLOR 10, 0: PRINT " "; : COLOR 9, 0: LOCATE 12, 3: PRINT "Hab Display:["; zp$(11); "]"; : COLOR 11, 0: INPUT "", Zpath11$
        IF Zpath11$ = "" THEN Zpath11$ = zp$(11)
        if len(Zpath11$)>24 then locate 11,1:print space$(79);:locate 11,1:goto 21
               
        a$ = Zpath1$+space$(25-len(Zpath1$)): PUT #1, 1, a$: IF Zpath1$ = "." THEN Zpath1$ = ""
        a$ = Zpath2$+space$(25-len(Zpath2$)): PUT #1, 2, a$: IF Zpath2$ = "." THEN Zpath2$ = ""
        a$ = Zpath3$+space$(25-len(Zpath3$)): PUT #1, 3, a$: IF Zpath3$ = "." THEN Zpath3$ = ""
        a$ = Zpath4$+space$(25-len(Zpath4$)): PUT #1, 4, a$: IF Zpath4$ = "." THEN Zpath4$ = ""
        a$ = Zpath5$+space$(25-len(Zpath5$)): PUT #1, 5, a$: IF Zpath5$ = "." THEN Zpath5$ = ""
        a$ = Zpath6$+space$(25-len(Zpath6$)): PUT #1, 6, a$: IF Zpath6$ = "." THEN Zpath6$ = ""
        a$ = Zpath7$+space$(25-len(Zpath7$)): PUT #1, 7, a$: IF Zpath7$ = "." THEN Zpath7$ = ""
        a$ = Zpath8$+space$(25-len(Zpath8$)): PUT #1, 8, a$: IF Zpath8$ = "." THEN Zpath8$ = ""
        a$ = Zpath9$+space$(25-len(Zpath9$)): PUT #1, 9, a$: IF Zpath9$ = "." THEN Zpath9$ = ""
        a$ = Zpath10$+space$(25-len(Zpath10$)): PUT #1, 10, a$: IF Zpath10$ = "." THEN Zpath10$ = ""
        a$ = Zpath11$+space$(25-len(Zpath11$)): PUT #1, 11, a$: IF Zpath11$ = "." THEN Zpath11$ = ""
        CLOSE #1

        tt = TIMER
        ttt = TIMER
        COLOR 9, 0
        LOCATE 1, 50: PRINT "READ";
        LOCATE 1, 65: PRINT "WRITE";
        locate 15,1:color 10,0:print "t";
       
100     if restartFLAG = 1 then 110
191     ERRflag=0
        OPEN "R", #1, Zpath10$ + "pirate.RND", 62
        if ERRflag=1 then ERRflag=2: LOCATE 12, 50: COLOR 12, 0: PRINT Zpath10$;:color 8,0:print "pirate";:goto 199
        ERRflag=2
        pirateSTR$=space$(62)
        GET #1, 1, pirateSTR$
        close #1
        chkCHAR1$=left$(pirateSTR$,1)
        chkCHAR2$=right$(pirateSTR$,1)
        if len(pirateSTR$) <> 62 then LOCATE 12, 50: COLOR 10, 0: PRINT Zpath10$;: color 12,0:print "pirate";:goto 199
        if chkCHAR1$<>chkCHAR2$ then COLOR 10, 0: LOCATE 12, 50: PRINT Zpath10$;: color 14,0:print "pirate";: goto 199
        LOCATE 12, 50: COLOR 10, 0: PRINT Zpath10$; "pirate"; 
        pirateSTR$=mid$(pirateSTR$,2,60)
'        Px38=cvd(mid$(pirateSTR$,3,8))
'        Py38=cvd(mid$(pirateSTR$,11,8))
'        Vx38=cvd(mid$(pirateSTR$,19,8))
'        Vy38=cvd(mid$(pirateSTR$,27,8))
'        locate 5,40:print Px38;
'        locate 6,40:print Py38;
'        locate 7,40:print Vx38;
'        locate 8,40:print Vy38;
'        locate 9,40:print len(pirateSTR$);

        active=cvi(mid$(pirateSTR$,1,2))
        pirateLOC$=mid$(pirateSTR$,3,32)
        activeAYSE=cvi(mid$(pirateSTR$,35,2))
        pirateANGLE$=mid$(pirateSTR$,37,8)

199     k=1
101     ERRflag=0
        OPEN "R", #1, Zpath1$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: LOCATE 2, 50: COLOR 12, 0: PRINT Zpath1$;:color 8,0:print "OSBACKUP";:goto 103
        ERRflag=2
        inpSTR1$=space$(1427)
        GET #1, 1, inpSTR1$
        close #1
        chkCHAR1$=left$(inpSTR1$,1)
        chkCHAR2$=right$(inpSTR1$,1)
        if len(inpSTR1$) <> 1427 then LOCATE 2, 50: COLOR 10, 0: PRINT Zpath1$;: color 12,0:print "OSBACKUP";:goto 103
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 2, 50: PRINT Zpath1$; "OSBACKUP";: goto 110
        k=k+1
        if k<4 then 101
        LOCATE 2, 50: COLOR 10, 0: PRINT Zpath1$;: color 14,0: print "OSBACKUP";
103     COLOR 8, 0: LOCATE 2, 65: PRINT Zpath2$ + "OSBACKUP";
        COLOR 8, 0: LOCATE 3, 65: PRINT Zpath3$ + "OSBACKUP";
        COLOR 8, 0: LOCATE 4, 65: PRINT Zpath4$ + "OSBACKUP";
        COLOR 8, 0: LOCATE 5, 65: PRINT Zpath7$ + "OSBACKUP";
        COLOR 8, 0: LOCATE 6, 65: PRINT Zpath8$ + "OSBACKUP";
        COLOR 8, 0: LOCATE 7, 65: PRINT Zpath9$ + "OSBACKUP";
        readERRORflag = 1: GOTO 300


110     'if active = 1 then mid$(inpSTR1$,1355,32) = pirateLOC$:mid$(inpSTR1$,1339,8) = pirateANGLE$:mid$(inpSTR1$,1347,8)=mkd$(1)
        'if active = 1 and activeAYSE = 150 then mid$(inpSTR1$,1163,32) = pirateLOC$
        'if active = 0 then mid$(inpSTR1$,1347,8)=mkd$(0)
        'locate 9,30:print cvd(mid$(pirateLOC$,1,8));
        'locate 10,30:print cvd(mid$(pirateLOC$,9,8));
        'locate 11,30:print cvd(mid$(pirateLOC$,17,8));
        'locate 12,30:print cvd(mid$(pirateLOC$,25,8));
        
        
        
        
        if TESTtime=1 then gosub 1400
        'locate 18,1:print "TESTtimer:";:print timer-TESTtimer;
        'TESTtimer = timer

        IF restartFLAG = 1 THEN z$ = "XXXXXYY"
        IF mirrreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXXX"
        IF mirrreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath2$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: LOCATE 2, 65: COLOR 12, 0: PRINT Zpath2$;: color 8,0: print "OSBACKUP";:goto 120
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 2, 65: PRINT Zpath2$; "OSBACKUP";

120     IF telreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXXX"
        IF telreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath3$ + "OSbackup.rnd", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 3, 65: PRINT Zpath3$;: color 8,0: print "OSBACKUP";:goto 130
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 3, 65: PRINT Zpath3$ + "OSBACKUP";

130     IF SIMreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXXX"
        IF SIMreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath4$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 4, 65: PRINT Zpath4$;: color 8,0: print "OSBACKUP";:goto 140
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 4, 65: PRINT Zpath4$ + "OSBACKUP";

140     IF esimreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXXX"
        IF esimreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath7$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 5, 65: PRINT Zpath7$;: color 8,0: print "OSBACKUP";:goto 150
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 5, 65: PRINT Zpath7$ + "OSBACKUP";

150     IF dispreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXXX"
        IF dispreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath8$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 6, 65: PRINT Zpath8$;: color 8,0: print "OSBACKUP";:goto 155
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 6, 65: PRINT Zpath8$ + "OSBACKUP";
155     ERRflag=0
        OPEN "R", #1, Zpath11$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 25, 65: PRINT Zpath11$;: color 8,0: print "OSBACKUP";:goto 160
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 25, 65: PRINT Zpath11$ + "OSBACKUP";



160     IF engreset = 1 AND restartFLAG = 0 THEN z$ = "XXXXXYY" '"XXXXXXX"
        IF engreset + restartFLAG = 0 THEN z$ = "ORBIT5S"
        mid$(inpSTR1$,2,7)=z$
        ERRflag=0
        OPEN "R", #1, Zpath9$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 7, 65: PRINT Zpath9$;: color 8,0: print "OSBACKUP";:goto 170
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 7, 65: PRINT Zpath9$ + "OSBACKUP";

170     mid$(inpSTR1$,2,7)="ORBIT5S"
        ERRflag=0
        OPEN "R", #1, Zpath10$ + "OSbackup.RND", 1427
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 8, 65: PRINT Zpath10$;: color 8,0: print "OSBACKUP";:goto 300
        ERRflag=2
        put #1, 1, inpSTR1$
        close #1
        COLOR 10, 0: LOCATE 8, 65: PRINT Zpath10$ + "OSBACKUP";


200     'OPEN "I", #1, Zpath3$ + "ORBITMC"
        'COLOR 10, 0: LOCATE 20, 1: PRINT Zpath3$ + "ORBITMC";
        'COLOR 10, 0: LOCATE 4, 50: PRINT Zpath3$ + "ORBITMC";
        'IF EOF(1) THEN CLOSE #1: COLOR 14, 0: LOCATE 21, 1: PRINT Zpath4$ + "ORBITMC"; : COLOR 12, 0: LOCATE 4, 50: PRINT Zpath3$ + "ORBITMC"; : readERRORflag = 1: GOTO 300
201     'INPUT #1, z$
        'CLOSE #1

210     'OPEN "O", #1, Zpath4$ + "ORBITMC"
        'COLOR 10, 0: LOCATE 21, 1: PRINT Zpath4$ + "ORBITMC";
        'COLOR 10, 0: LOCATE 12, 65: PRINT Zpath4$ + "ORBITMC";
211     'PRINT #1, z$
        'CLOSE #1
      



300     if restartFLAG = 1 then 310
        k=1
301     ERRflag=0
        OPEN "R", #1, Zpath4$ + "ORB5res.RND", 412
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 3, 50: PRINT Zpath4$;: color 8,0: print "ORB5RES";:goto 303
        ERRflag=2
        inpSTR2$=space$(412)
        Get #1, 1, inpSTR2$
        close #1
        chkCHAR1$=left$(inpSTR2$,1)
        chkCHAR2$=right$(inpSTR2$,1)
        if len(inpSTR2$) <> 412 then LOCATE 3, 50: COLOR 10, 0: PRINT Zpath4$;: color 12,0:print "ORB5RES";:goto 303
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 3, 50: PRINT Zpath4$; "ORB5RES";: goto 310
        k=k+1
        if k<4 then 301
        LOCATE 3, 50: COLOR 10, 0: PRINT Zpath4$;: color 14,0: print "ORB5RES";
303     COLOR 8, 0: LOCATE 9, 65: PRINT Zpath9$ + "ORB5RES";
        COLOR 8, 0: LOCATE 10, 65: PRINT Zpath3$ + "ORB5RES";
        readERRORflag = 1: GOTO 400
        

310     IF RCload = 0 THEN 312
        Rt = cvi(mid$(inpSTR2$,256,2))                          'VAL(z$(407))
        Rt = Rt + (RCload * 4)
        mid$(inpSTR2$,256,2) = mki$(Rt)                               'z$(407) = STR$(Rt)
312     IF FCenable = 0 THEN mid$(inpSTR2$,294,2) = mki$(3)     'z$(382) = "3"
        ERRflag=0
        OPEN "R", #1, Zpath9$ + "ORB5res.RND", 412
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 9, 65: PRINT Zpath9$;: color 8,0: print "ORB5RES";:goto 320
        ERRflag=2
        put #1, 1, inpSTR2$
        close #1
        COLOR 10, 0: LOCATE 9, 65: PRINT Zpath9$ + "ORB5RES";

        
320     ERRflag=0
        OPEN "R", #1, Zpath3$ + "ORB5res.RND", 412
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 10, 65: PRINT Zpath3$;: color 8,0: print "ORB5RES";:goto 400
        ERRflag=2
        put #1, 1, inpSTR2$
        close #1
        COLOR 10, 0: LOCATE 10, 65: PRINT Zpath3$ + "ORB5RES";



400     if restartFLAG = 1 then 410
        k=1
401     ERRflag=0
        OPEN "R", #1, Zpath5$ + "GASTELEMETRY.RND", 800
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 4, 50: PRINT Zpath5$;: color 8,0: print "GASTELEM";:goto 403
        ERRflag=2
        inpSTR3$=space$(800)
        Get #1, 1, inpSTR3$
        close #1
        chkCHAR1$=left$(inpSTR3$,1)
        chkCHAR2$=right$(inpSTR3$,1)
        if len(inpSTR3$) <> 800 then LOCATE 4, 50: COLOR 10, 0: PRINT Zpath5$;: color 12,0:print "GASTELEM";:goto 403
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 4, 50: PRINT Zpath5$; "GASTELEM";: goto 410
        k=k+1
        if k<4 then 401
        LOCATE 4, 50: COLOR 10, 0: PRINT Zpath5$;: color 14,0: print "GASTELEM";
403     COLOR 8, 0: LOCATE 11, 65: PRINT Zpath6$ + "GASTELEM";
        COLOR 8, 0: LOCATE 12, 65: PRINT Zpath7$ + "GASTELEM";
        readERRORflag = 1: GOTO 500

410     probe = 0
        PROBEflag = cvs(mid$(inpSTR3$,324,4))
        IF PROBEflag = -10 THEN probe = 1': z$(513) = z$(512)
        IF PROBEflag = -20 THEN probe = 2': z$(513) = z$(512)
        RCload = cvs(mid$(inpSTR3$,252,4))   'VAL(z$(497)) / 10
        FCenable = 0
        O2a1 = cvs(mid$(inpSTR3$, 400, 4))
        O2a2 = cvs(mid$(inpSTR3$, 404, 4))
        O2b1 = cvs(mid$(inpSTR3$, 416, 4))
        O2b2 = cvs(mid$(inpSTR3$, 420, 4))
        IF O2a1 > 0 AND O2a2 = 1 THEN FCenable = 1
        IF O2b1 > 0 AND O2b2 = 1 THEN FCenable = 1

        ERRflag=0
        OPEN "R", #1, Zpath6$ + "GASTELEMETRY.RND", 800
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 11, 65: PRINT Zpath6$;: color 8,0: print "GASTELEM";:goto 420
        ERRflag=2
        put #1, 1, inpSTR3$
        close #1
        COLOR 10, 0: LOCATE 11, 65: PRINT Zpath6$ + "GASTELEM";

420     ERRflag=0
        OPEN "R", #1, Zpath7$ + "GASTELEMETRY.RND", 800
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 12, 65: PRINT Zpath7$;: color 8,0: print "GASTELEM";:goto 500
        ERRflag=2
        put #1, 1, inpSTR3$
        close #1
        COLOR 10, 0: LOCATE 12, 65: PRINT Zpath7$ + "GASTELEM";





500     if restartFLAG = 1 then 510
        k=1
501     ERRflag=0
        OPEN "R", #1, Zpath6$ + "GASMC.RND", 82
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 5, 50: PRINT Zpath6$;: color 8,0: print "GASMC";:goto 503
        ERRflag=2
        inpSTR4$=space$(82)
        Get #1, 1, inpSTR4$
        close #1
        chkCHAR1$=left$(inpSTR4$,1)
        chkCHAR2$=right$(inpSTR4$,1)
        if len(inpSTR4$) <> 82 then LOCATE 5, 50: COLOR 10, 0: PRINT Zpath6$;: color 12,0:print "GASMC";:goto 503
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 5, 50: PRINT Zpath6$; "GASMC";: goto 510
        k=k+1
        if k<4 then 501
        LOCATE 5, 50: COLOR 10, 0: PRINT Zpath6$;: color 14,0: print "GASMC";
503     COLOR 8, 0: LOCATE 13, 65: PRINT Zpath5$ + "GASMC";
        COLOR 8, 0: LOCATE 14, 65: PRINT Zpath7$ + "GASMC";
        readERRORflag = 1: GOTO 600



510     ERRflag=0
        OPEN "R", #1, Zpath5$ + "GASMC.RND", 82
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 13, 65: PRINT Zpath5$;: color 8,0: print "GASMC";:goto 520
        ERRflag=2
        put #1, 1, inpSTR4$
        close #1
        COLOR 10, 0: LOCATE 13, 65: PRINT Zpath5$ + "GASMC";

520     ERRflag=0
        OPEN "R", #1, Zpath7$ + "GASMC.RND", 82
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 14, 65: PRINT Zpath7$;: color 8,0: print "GASMC";:goto 600
        ERRflag=2
        put #1, 1, inpSTR4$
        close #1
        COLOR 10, 0: LOCATE 14, 65: PRINT Zpath7$ + "GASMC";



600     if restartFLAG = 1 then 610
        k=1
601     ERRflag=0
        OPEN "R", #1, Zpath7$ + "GASSIM.RND", 182
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 6, 50: PRINT Zpath7$;: color 8,0: print "GASSIM";:goto 603
        ERRflag=2
        inpSTR5$=space$(182)
        Get #1, 1, inpSTR5$
        close #1
        chkCHAR1$=left$(inpSTR5$,1)
        chkCHAR2$=right$(inpSTR5$,1)
        if len(inpSTR5$) <> 182 then LOCATE 6, 50: COLOR 10, 0: PRINT Zpath7$;: color 12,0:print "GASSIM";:goto 603
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 6, 50: PRINT Zpath7$; "GASSIM";: goto 610
        k=k+1
        if k<4 then 601
        LOCATE 6, 50: COLOR 10, 0: PRINT Zpath7$;: color 14,0: print "GASSIM";
603     COLOR 8, 0: LOCATE 15, 65: PRINT Zpath5$ + "GASSIM";
        readERRORflag = 1: GOTO 700

610     ERRflag=0
        OPEN "R", #1, Zpath5$ + "GASSIM.RND", 182
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 15, 65: PRINT Zpath5$;: color 8,0: print "GASSIM";:goto 700
        ERRflag=2
        put #1, 1, inpSTR5$
        locate 13, 1:color 10, 0: print "x ";:color 9, 0:print "change drives";
        close #1
        COLOR 10, 0: LOCATE 15, 65: PRINT Zpath5$ + "GASSIM";



700     if restartFLAG = 1 then 710
        k=1
701     ERRflag=0
        OPEN "R", #1, Zpath7$ + "DOORSIM.RND", 276
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 7, 50: PRINT Zpath7$;: color 8,0: print "DOORSIM";:goto 703
        ERRflag=2
        inpSTR6$=space$(276)
        Get #1, 1, inpSTR6$
        close #1
        chkCHAR1$=left$(inpSTR6$,1)
        chkCHAR2$=right$(inpSTR6$,1)
        if len(inpSTR6$) <> 276 then LOCATE 7, 50: COLOR 10, 0: PRINT Zpath7$;: color 12,0:print "DOORSIM";:goto 703
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 7, 50: PRINT Zpath7$; "DOORSIM";: goto 710
        k=k+1
        if k<4 then 701
        LOCATE 7, 50: COLOR 10, 0: PRINT Zpath7$;: color 14,0: print "DOORSIM";
703     COLOR 8, 0: LOCATE 16, 65: PRINT Zpath5$ + "DOORSIM";
        readERRORflag = 1: GOTO 800

710     mid$(inpSTR6$,270,2) = mki$(RCblock)
        mid$(inpSTR6$,272,4) = mks$(IS2)
        mid$(inpSTR6$,268,2) = mki$(PACKblock) 'IF PACKblock = 1 THEN ENVy# = VAL(z$(760)): ENVy# = ENVy# + 64: z$(760) = STR$(ENVy#)
        ERRflag=0
        OPEN "R", #1, Zpath5$ + "DOORSIM.RND", 276
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 16, 65: PRINT Zpath5$;: color 8,0: print "DOORSIM";:goto 800
        ERRflag=2
        put #1, 1, inpSTR6$
        close #1
        COLOR 10, 0: LOCATE 16, 65: PRINT Zpath5$ + "DOORSIM";



800     if restartFLAG = 1 then 810
        k=1
801     ERRflag=0
        OPEN "R", #1, Zpath9$ + "ORBITSSE.RND", 1159
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 8, 50: PRINT Zpath9$;: color 8,0: print "ORBITSSE";:goto 803
        ERRflag=2
        inpSTR7$=space$(1159)
        Get #1, 1, inpSTR7$
        close #1
        chkCHAR1$=left$(inpSTR7$,1)
        chkCHAR2$=right$(inpSTR7$,1)
        if len(inpSTR7$) <> 1159 then LOCATE 8, 50: COLOR 10, 0: PRINT Zpath9$;: color 12,0:print "ORBITSSE";:goto 803
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 8, 50: PRINT Zpath9$; "ORBITSSE";: goto 810
        k=k+1
        if k<4 then 801
        LOCATE 8, 50: COLOR 10, 0: PRINT Zpath9$;: color 14,0: print "ORBITSSE";
803     COLOR 8, 0: LOCATE 17, 65: PRINT Zpath1$ + "ORBITSSE";
        COLOR 8, 0: LOCATE 18, 65: PRINT Zpath3$ + "ORBITSSE";
        COLOR 8, 0: LOCATE 19, 65: PRINT Zpath4$ + "ORBITSSE";
        COLOR 8, 0: LOCATE 20, 65: PRINT Zpath10$ + "ORBITSSE";
        readERRORflag = 1: GOTO 900

810     temp$ = mid$(inpSTR7$,208,8)
        
        'locate 3,30:print probe;
        IF flightreset = 1 THEN mid$(inpSTR7$,202,8) = mkd$(8)
        IF restartFLAG = 1 THEN mid$(inpSTR7$,202,8) = mkd$(24)
        IF probe = 0 THEN mid$(inpSTR7$,130,8) = mkd$(0)' z$(857) = "0"
        IF probe = 1 THEN mid$(inpSTR7$,130,8) = mkd$(1)'z$(857) = "1": z$(858) = "28"
        IF probe = 1 THEN mid$(inpSTR7$,138,8) = mkd$(28)
        IF probe = 2 THEN mid$(inpSTR7$,130,8) = mkd$(2)'z$(857) = "2"
        EL6 = cvs(mid$(inpSTR7$,231,4))
        switch1 = cvi(mid$(inpSTR7$,279,2))
        EL1 = cvs(mid$(inpSTR7$,211,4))
        IS2 = cvs(mid$(inpSTR7$,215,4))
        PBflag = cvs(mid$(inpSTR7$,689,4))
        RCblock = 1
        'locate 1,30:print EL6;
        'locate 2,30:print switch1;
        'locate 3,30:print EL1;
        IF EL6 > 9000 AND switch1 = 1 AND EL1 > 10 THEN RCblock = 0
        PACKblock = 1
        IF PBflag = 9 THEN PACKblock = 0
        
        pirateTEMP$=mid$(inpSTR7$,219,60)
        mid$(inpSTR7$,219,60) = pirateSTR$
        'Px38=cvd(mid$(inpSTR7$,221,8))
        'Py38=cvd(mid$(inpSTR7$,229,8))
        'Vx38=cvd(mid$(inpSTR7$,237,8))
        'Vy38=cvd(mid$(inpSTR7$,245,8))
        'locate 2,30:print Px38;
        'locate 3,30:print Py38;
        'locate 4,30:print Vx38;
        'locate 5,30:print Vy38;
'        locate 6,30:print cvd(mid$(inpSTR7$,255,8))
'        locate 7,30:print cvd(mid$(inpSTR7$,263,8))
'        locate 8,30:print cvd(mid$(inpSTR7$,271,8))

        

        ERRflag=0
        OPEN "R", #1, Zpath1$ + "ORBITSSE.RND", 1159
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 17, 65: PRINT Zpath1$;: color 8,0: print "ORBITSSE";:goto 820
        ERRflag=2
        put #1, 1, inpSTR7$
        close #1
        COLOR 10, 0: LOCATE 17, 65: PRINT Zpath1$ + "ORBITSSE";

820     mid$(inpSTR7$,219,60) = pirateTEMP$
        mid$(inpSTR7$,208,8)=temp$    'z$(866) = temp$
        ERRflag=0
        OPEN "R", #1, Zpath3$ + "ORBITSSE.RND", 1159
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 18, 65: PRINT Zpath3$;: color 8,0: print "ORBITSSE";:goto 830
        ERRflag=2
        put #1, 1, inpSTR7$
        close #1
        COLOR 10, 0: LOCATE 18, 65: PRINT Zpath3$ + "ORBITSSE";
        
830     ERRflag=0
        OPEN "R", #1, Zpath10$ + "ORBITSSE.RND", 1159
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 20, 65: PRINT Zpath10$;: color 8,0: print "ORBITSSE";:goto 840
        ERRflag=2
        put #1, 1, inpSTR7$
        close #1
        COLOR 10, 0: LOCATE 20, 65: PRINT Zpath10$ + "ORBITSSE";

840     ERRflag=0
        OPEN "R", #1, Zpath4$ + "ORBITSSE.RND", 1159
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 19, 65: PRINT Zpath4$;: color 8,0: print "ORBITSSE";:goto 900
        ERRflag=2
        put #1, 1, inpSTR7$
        close #1
        COLOR 10, 0: LOCATE 19, 65: PRINT Zpath4$ + "ORBITSSE";



900     if restartFLAG = 1 then 910
        k=1
901     ERRflag=0
        OPEN "R", #1, Zpath8$ + "MST.RND", 26
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 9, 50: PRINT Zpath8$;: color 8,0: print "MST";:goto 903
        ERRflag=2
        inpSTR8$=space$(26)
        Get #1, 1, inpSTR8$
        close #1
        chkCHAR1$=left$(inpSTR8$,1)
        chkCHAR2$=right$(inpSTR8$,1)
        if len(inpSTR8$) <> 26 then LOCATE 9, 50: COLOR 10, 0: PRINT Zpath8$;: color 12,0:print "MST";:goto 903
        if chkCHAR1$=chkCHAR2$ then COLOR 10, 0: LOCATE 9, 50: PRINT Zpath8$; "MST";: goto 910
        k=k+1
        if k<4 then 901
        LOCATE 9, 50: COLOR 10, 0: PRINT Zpath8$;: color 14,0: print "MST";
903     COLOR 8, 0: LOCATE 21, 65: PRINT Zpath1$ + "MST";
        COLOR 8, 0: LOCATE 22, 65: PRINT Zpath2$ + "MST";
        readERRORflag = 1: GOTO 900
        
910     ERRflag=0
        OPEN "R", #1, Zpath1$ + "MST.RND", 26
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 21, 65: PRINT Zpath1$;: color 8,0: print "MST";:goto 920
        ERRflag=2
        put #1, 1, inpSTR8$
        close #1
        COLOR 10, 0: LOCATE 21, 65: PRINT Zpath1$ + "MST";

920     ERRflag=0
        OPEN "R", #1, Zpath2$ + "MST.RND", 26
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 22, 65: PRINT Zpath2$;: color 8,0: print "MST";:goto 930
        ERRflag=2
        put #1, 1, inpSTR8$
        close #1
        COLOR 10, 0: LOCATE 22, 65: PRINT Zpath2$ + "MST";

930     chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        if TESTtime=1 then 931
        timestamp$=mid$(inpSTR1$,89,16)
        yearC=cvi(mid$(timestamp$,1,2))
        dayC=cvi(mid$(timestamp$,3,2))
        hrC=cvi(mid$(timestamp$,5,2))
        minC=cvi(mid$(timestamp$,7,2))
        secC=cvd(mid$(timestamp$,9,8))
931     outSTR$=chr$(chkBYTE)+timestamp$+space$(8)+chr$(chkBYTE)
        IF eecomreset = 1 THEN outSTR$ = chr$(chkBYTE)+"XXXXXXX                 "+chr$(chkBYTE)
        IF restartFLAG = 1 THEN outSTR$ = chr$(chkBYTE)+"XXXXXYY                 "+chr$(chkBYTE)
        ERRflag=0
        OPEN "R", #1, Zpath5$ + "TIME.RND", 26
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 23, 65: PRINT Zpath5$;: color 8,0: print "TIME";:goto 940
        ERRflag=2
        put #1, 1, outSTR$
        close #1
        COLOR 10, 0: LOCATE 23, 65: PRINT Zpath5$ + "TIME";

940     outSTR$=chr$(chkBYTE)+timestamp$+space$(8)+chr$(chkBYTE)
        IF eecomMCreset = 1 THEN outSTR$ = chr$(chkBYTE)+"XXXXXXX                 "+chr$(chkBYTE)
        IF restartFLAG = 1 THEN outSTR$ = chr$(chkBYTE)+"XXXXXYY                 "+chr$(chkBYTE)
        ERRflag=0
        OPEN "R", #1, Zpath6$ + "TIME.RND", 26
        if ERRflag=1 then ERRflag=2: COLOR 12, 0: LOCATE 24, 65: PRINT Zpath6$;: color 8,0: print "TIME";:goto 1000
        ERRflag=2
        put #1, 1, outSTR$
        close #1
        COLOR 10, 0: LOCATE 24, 65: PRINT Zpath6$ + "TIME";



1000    IF flightreset = 1 THEN flightreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 2, 3: PRINT "Flight": COLOR 7, 0
        IF engreset = 1 THEN engreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 10, 3: PRINT "Hab Eng": COLOR 7, 0
        IF telreset = 1 THEN telreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 4, 3: PRINT "Telemetry": COLOR 7, 0
        IF dispreset = 1 THEN dispreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 6, 3: PRINT "Display": COLOR 7, 0
        IF eecomreset = 1 THEN eecomreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 7, 3: PRINT "Hab EECOM": COLOR 7, 0
        IF eecomMCreset = 1 THEN eecomMCreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 8, 3: PRINT "Hab EECOM": COLOR 7, 0
        IF esimreset = 1 THEN esimreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 9, 3: PRINT "SIM EECOM": COLOR 7, 0
        IF SIMreset = 1 THEN SIMreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 5, 3: PRINT "Simulator": COLOR 7, 0
        IF mirrreset = 1 THEN mirrreset = 0: resetFLAG = 1: COLOR 9, 0: LOCATE 3, 3: PRINT "Mirror": COLOR 7, 0
        IF restartFLAG = 1 THEN restartFLAG = 0: resetFLAG = 1: knt = RESETknt: locate 13,3: color 9, 0: print "SYSTEM RESET";
        IF resetFLAG = 1 THEN resetFLAG = 0: ttt = ttt + 5  

        'IF ttt > 86400 THEN ttt = ttt - 86400
        LOCATE 16, 3: COLOR 9, 0: PRINT "Backup:";
        LOCATE 17, 3: COLOR readERRORflag * 9, 0: PRINT "READ ERROR";
        'COLOR 9, 0: LOCATE 23, 50: PRINT "Time to backup: "; : COLOR 11, 0: PRINT USING "#####.#"; 5 - (TIMER - tt);
        LOCATE 15, 3
        COLOR 11+(3*TESTtime), 0: PRINT using "####"; yearC;
        COLOR 9, 0: PRINT ":";
        COLOR 11+(3*TESTtime), 0: PRINT using "###"; dayC;
        COLOR 9, 0: PRINT ":";
        COLOR 11+(3*TESTtime), 0: PRINT using "##"; hrC;
        COLOR 9, 0: PRINT ":";
        COLOR 11+(3*TESTtime), 0: PRINT using "##"; minC;
        COLOR 9, 0: PRINT ":";
        COLOR 11+(3*TESTtime), 0: PRINT USING "##"; secC;

        IF backupFLAG < 1 THEN 1002
        IF readERRORflag > .1 THEN 1002

        LOCATE 16, 3: COLOR 11, 0: PRINT "Backup";
        tt = TIMER
        'LOCATE 18, 50: PRINT TIMER;
        outSTR$=inpSTR1$+inpSTR2$+inpSTR3$+inpSTR4$+inpSTR5$+inpSTR6$+inpSTR7$+inpSTR8$
        knt=knt+1
        if knt=1 then mid$(outSTR$,10,4)=mkl$(knt)
        Put #5, knt, outSTR$
        if knt=1 then 1009 
        GET #5, 1, outSTR$
        mid$(outSTR$,10,4)=mkl$(knt)
        put #5, 1, outSTR$
        
1009    LOCATE 16, 11: COLOR 11, 0: PRINT USING "######"; knt;
        IF NEWknt = 0 THEN NEWknt = 1: RESETknt = knt: GOSUB 1200


1002    readERRORflag = 0
        color 9, 0
        LOCATE 20, 1: cycle = 1 - cycle: PRINT CHR$(47 + (cycle * 45));
        cycleTIME=TIMER-ttt
        if cycleTIME>999.9999 then cycleTIME=999.9999
        LOCATE 20, 3: PRINT "Cycle Time:"; : COLOR 11, 0: PRINT USING "###.####"; cycleTIME;
1005    z$ = INKEY$
        IF z$ = CHR$(27) THEN CLOSE #5: END
        if len(z$)<2 then 1015
        IF z$ = CHR$(0) + "Q" AND RESETknt < knt - 1 THEN RESETknt = RESETknt + 1: GOSUB 1200 : goto 1014
        IF z$ = CHR$(0) + "O" AND RESETknt > 1 THEN RESETknt = RESETknt - 1: GOSUB 1200: goto 1014
        IF z$ = CHR$(0) + "M" AND RESETknt < knt - 10 THEN RESETknt = RESETknt + 10: GOSUB 1200: goto 1014
        IF z$ = CHR$(0) + "K" AND RESETknt > 10 THEN RESETknt = RESETknt - 10: GOSUB 1200: goto 1014
        IF z$ = CHR$(0) + "I" AND RESETknt < knt - 100 THEN RESETknt = RESETknt + 100: GOSUB 1200: goto 1014
        IF z$ = CHR$(0) + "G" AND RESETknt > 100 THEN RESETknt = RESETknt - 100: GOSUB 1200: goto 1014
        IF z$ = CHR$(0) + "L" AND knt > 1 THEN RESETknt = knt - 1: GOSUB 1200
1014    if TIMER - ttt < .8 then 1005 else 1004
1015    IF z$ = "a" THEN flightreset = 1: COLOR 12, 0: LOCATE 2, 3: PRINT "Flight": COLOR 7, 0
        IF z$ = "i" THEN engreset = 1: COLOR 12, 0: LOCATE 10, 3: PRINT "Hab Eng": COLOR 7, 0
        IF z$ = "c" THEN telreset = 1: COLOR 12, 0: LOCATE 4, 3: PRINT "Telemetry": COLOR 7, 0
        IF z$ = "e" THEN dispreset = 1: COLOR 12, 0: LOCATE 6, 3: PRINT "Display": COLOR 7, 0
        IF z$ = "f" THEN eecomreset = 1: COLOR 12, 0: LOCATE 7, 3: PRINT "Hab EECOM": COLOR 7, 0
        IF z$ = "g" THEN eecomMCreset = 1: COLOR 12, 0: LOCATE 8, 3: PRINT "MC EECOM": COLOR 7, 0
        IF z$ = "d" THEN SIMreset = 1: COLOR 12, 0: LOCATE 5, 3: PRINT "Simulator": COLOR 7, 0
        IF z$ = "h" THEN esimreset = 1: COLOR 12, 0: LOCATE 9, 3: PRINT "SIM EECOM": COLOR 7, 0
        IF z$ = "b" THEN mirrreset = 1: COLOR 12, 0: LOCATE 3, 3: PRINT "Mirror": COLOR 7, 0
        if z$ = "t" then TESTtime=1-TESTtime:color 14*TESTtime, 0:locate 15,21: PRINT "Internal Time";: COLOR 7, 0
        if z$="t" and TESTtime=1 then gosub 1450
        if ucase$(z$) = "X" then goto 1300
        IF z$ <> "r" THEN 1004
        restartFLAG = 1
       
        
        inpSTR$=space$(4364)
        GET #5, RESETknt, inpSTR$
        inpSTR1$ = mid$(inpSTR$, 1, 1427)
        inpSTR2$ = mid$(inpSTR$, 1428, 412)
        inpSTR3$ = mid$(inpSTR$, 1840, 800)
        inpSTR4$ = mid$(inpSTR$, 2640, 82)
        inpSTR5$ = mid$(inpSTR$, 2722, 182)
        inpSTR6$ = mid$(inpSTR$, 2904, 276)
        inpSTR7$ = mid$(inpSTR$, 3180, 1159)
        inpSTR8$ = mid$(inpSTR$, 4339, 26)
        
        OPEN "R", #1, Zpath1$ + "RESTART.RND", 1427
        Put #1, 1, inpSTR1$
        CLOSE #1

        OPEN "R", #1, Zpath4$ + "engsimrs.RND", 412
        Put #1, 1, inpSTR2$
        CLOSE #1

        OPEN "R", #1, Zpath5$ + "EECOMrs.RND", 800
        Put #1, 1, inpSTR3$
        CLOSE #1

        OPEN "R", #1, Zpath7$ + "gasRS1.RND", 182
        Put #1, 1, inpSTR5$
        CLOSE #1

        OPEN "R", #1, Zpath7$ + "gasRS2.RND", 276
        Put #1, 1, inpSTR6$
        CLOSE #1

        OPEN "R", #1, Zpath9$ + "resetSSE.RND", 1159
        Put #1, 1, inpSTR7$
        CLOSE #1

        OPEN "R", #1, Zpath8$ + "MSTrs.RND", 26
        Put #1, 1, inpSTR8$
        CLOSE #1

        OPEN "R", #1, Zpath6$ + "GASMCrs.RND", 82
        Put #1, 1, inpSTR4$
        CLOSE #1



1004    COLOR 9, 0
        'ycle = 1 - cycle
        'OCATE 19, 1: PRINT using "##"; CHR$(47 + (cycle * 45)); ' " "; CHR$(47 + (cycle * 45));
        'OCATE 20, 4: PRINT "Cycle Time:"; : COLOR 11, 0: PRINT USING "###.####"; TIMER - ttt;
        'OLOR 9, 0
        backupFLAG = 0
1003    IF TIMER - tt > 5 THEN backupFLAG = 1
1001    IF TIMER - ttt > .9999 THEN ttt = TIMER: GOTO 100
        IF TIMER - ttt < -10 THEN ttt = TIMER
        GOTO 1001




1200    LOCATE 22, 1: COLOR 10, 0: PRINT "r";
        LOCATE 22, 3: COLOR 9, 0: PRINT "Reset:  ";
        COLOR 11, 0: PRINT USING "######"; RESETknt;
        COLOR 9, 0: PRINT ":  ";
        inpSTR$=space$(4364)
        GET #5, RESETknt, inpSTR$
        timestamp$=mid$(inpSTR$,89,16)
        yearB=cvi(mid$(timestamp$,1,2))
        dayB=cvi(mid$(timestamp$,3,2))
        hrB=cvi(mid$(timestamp$,5,2))
        minB=cvi(mid$(timestamp$,7,2))
        secB=cvd(mid$(timestamp$,9,8))
        COLOR 11, 0: PRINT USING "####"; yearB;
        COLOR 9, 0: PRINT ":";
        COLOR 11, 0: PRINT USING "###"; dayB;
        COLOR 9, 0: PRINT ":";
        COLOR 11, 0: PRINT USING "##"; hrB;
        COLOR 9, 0: PRINT ":";
        COLOR 11, 0: PRINT USING "##"; minB;
        COLOR 9, 0: PRINT ":";
        COLOR 11, 0: PRINT USING "##"; secB;
        RETURN

1300    zp$(1) = Zpath1$
        zp$(2) = Zpath2$
        zp$(3) = Zpath3$
        zp$(4) = Zpath4$
        zp$(5) = Zpath5$
        zp$(6) = Zpath6$
        zp$(7) = Zpath7$
        zp$(8) = Zpath8$
        zp$(9) = Zpath9$
        zp$(10) = Zpath10$
        for i=2 to 11
         locate i,1: print space$(45);
        next i
        locate 2, 1
        OPEN "R", #1, "sevpath.RND", 25
        inpSTR$=space$(25)
        goto 11

         
1400    secC = secC + 1
        if secC >= 60 then secC = secC-60:minC = minC + 1
        if minC >= 60 then minC = minC-60:hrC = hrC + 1
        if hrC >= 24 then hrC = hrC-24:dayC = dayC + 1
        if dayC > 365 then dayC = dayC-365:yearC = yearC + 1
        timestamp$ = mki$(yearC)
        timestamp$ = timestamp$ + mki$(dayC)
        timestamp$ = timestamp$ + mki$(hrC)
        timestamp$ = timestamp$ + mki$(minC)
        timestamp$ = timestamp$ + mkd$(secC)
        mid$(inpSTR1$,89,16) = timestamp$
        return

1450    timestamp$=mid$(inpSTR1$,89,16)
        yearC=cvi(mid$(timestamp$,1,2))
        dayC=cvi(mid$(timestamp$,3,2))
        hrC=cvi(mid$(timestamp$,5,2))
        minC=cvi(mid$(timestamp$,7,2))
        secC=cvd(mid$(timestamp$,9,8))
        return


2000    if ERRflag=0 then ERRflag=1:resume next
        CLS
        LOCATE 22, 50: PRINT "error line: "; ERL;
        LOCATE 23, 50: PRINT "error code: "; ERR;
        z$=input$(1)
        END




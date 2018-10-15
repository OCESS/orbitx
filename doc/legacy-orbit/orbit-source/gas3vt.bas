        ON ERROR GOTO 2000
        DIM TEMP(10), a(6), c(7), ch(7, 29), d(9), dr(10, 5), n(6, 10), dw(8), de(8), da(10, 16), P(39, 2), chBASE(39, 8), ASTROrad(8), FIRE(10), ASTROstat(16)
        DIM GT(8, 2), tank(12), tankRC(10), health%(8, 7), PR(5), nO2(6)
       
        CLS
        color 7,0
        locate 1,1,0
11      OPEN "I", #1, "eecomINI"
        INPUT #1, ASTROtotal
        FOR i = 0 TO 39
         INPUT #1, P(i, 0), P(i, 1), P(i, 2)
         FOR j = 1 TO 8
          INPUT #1, chBASE(i, j)
         NEXT j
        NEXT i
        FOR i = 0 TO 6
         INPUT #1, a(i)
         INPUT #1, c(i)
         INPUT #1, ch(i, 9), ch(i, 12), ch(i, 13)
        NEXT i
        FOR i = 0 TO 8
         INPUT #1, da(i, 3), da(i, 4)
         INPUT #1, d(i + 1)
         FOR j = 1 TO 5
          INPUT #1, dr(i, j)
         NEXT j
         INPUT #1, ASTROstat(i)
        NEXT i
        FOR i = 1 TO 7
         FOR j = 11 TO 14
           INPUT #1, da(i, j)
         NEXT j
        NEXT i
        FOR i = 1 TO 84
         INPUT #1, x, y, z
         LOCATE y, x: PRINT CHR$(z);
        NEXT i
        FOR i = 1 TO 8
         INPUT #1, da(i, 0), da(i, 1), da(i, 2), da(i, 15), da(i, 16)
        NEXT i
        CLOSE #1
        PR(1) = 3
        PR(2) = 10
        PR(3) = 10
        PR(4) = 10
        cmp = 1
        tnk = 1
        pack = 1
        ASTRO = 1
        door = 1
        GOSUB 98
        gosub 8200

        COLOR 9, 0: LOCATE 21, 68: PRINT CHR$(17); CHR$(16); ": "; : COLOR 11, 0: PRINT "door";
        COLOR 9, 0: LOCATE 22, 69: PRINT CHR$(205); ": "; : COLOR 11, 0: PRINT "opn/cls";
        COLOR 9, 0: LOCATE 21, 57: PRINT CHR$(18); ": "; : COLOR 11, 0: PRINT "comp";
        COLOR 9, 0: LOCATE 22, 57: PRINT CHR$(241); ": "; : COLOR 11, 0: PRINT "press";
        COLOR 9, 0: LOCATE 23, 57: PRINT "$: "; : COLOR 11, 0: PRINT "ALvent";
        COLOR 9, 0: LOCATE 24, 57: PRINT CHR$(217); ": "; : COLOR 11, 0: PRINT "alarm";
        COLOR 9, 0: LOCATE 25, 57: PRINT "x: "; : COLOR 11, 0: PRINT "decon";
        COLOR 9, 0: LOCATE 23, 69: PRINT CHR$(180); ": "; : COLOR 11, 0: PRINT "astro sel";
        COLOR 9, 0: LOCATE 11, 18: PRINT "Ins: ";
        COLOR 9, 0: LOCATE 11, 47: PRINT "Del: ";
        COLOR 9, 0: LOCATE 25, 69: PRINT "\: "; : COLOR 11, 0: PRINT "alt. menu";
        COLOR 9, 0: LOCATE 24, 69: PRINT CHR$(195); ": "; : COLOR 11, 0: PRINT "tank sel";
        
13      OPEN "R", #1, "time.rnd",26
        inpSTR$=space$(26)
        Get #1, 1, inpSTR$
        'inpSTR$="AXXXXXXX                 A"
        z$=mid$(inpSTR$,2,7)
        if left$(z$,1)<>"X" then 2
        inpSTR$="A"+space$(24)+"A"
        put #1, 1, inpSTR$
2       close #1
        IF z$ = "XXXXXYY" THEN GOSUB 6000 else gosub 6010
        FOR i = 1 TO 6
         FOR j = 1 TO 6
          IF n(i, j) < 0 THEN n(i, j) = 0
          ch(i, j) = (n(i, j) * 8.31 * (TEMP(i)) / ch(i, 9)) / ch(i, 0)
         NEXT j
         '**IF n(i, 6) < 0 THEN n(i, 6) = 0
         IF n(i, 7) < 0 THEN n(i, 7) = 0
         IF n(i, 8) < 0 THEN n(i, 8) = 0
         '**ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i
        COLOR 7, 0
        'GOSUB 200
        
       
1       ttt = TIMER
        j = 0
        IF GT(2, 0) > .0004 AND GT(2, 1) = 1 THEN j = 2
        IF GT(1, 0) > .0004 AND GT(1, 1) = 1 THEN j = 1
        IF j = 0 THEN 8
        IF tankRC(1) > 0 AND tank(tankRC(1)) < 100 THEN tank(tankRC(1)) = tank(tankRC(1)) + .25: GT(j, 0) = GT(j, 0) - .00065
        IF tankRC(2) > 0 AND tank(tankRC(2)) < 100 THEN tank(tankRC(2)) = tank(tankRC(2)) + .25: GT(j, 0) = GT(j, 0) - .00065
8       FOR i = 1 TO 8
         IF (ASTROstat(i + 8) AND 1) = 0 THEN 3
         tank1 = (ASTROstat(i) AND 8190)
         tank2 = (ASTROstat(i) AND 33546240)
         IF tank1 < 1 THEN tank1 = 0 ELSE tank1 = CINT(LOG(tank1) * 1.442695)
         IF tank2 < 1 THEN tank2 = 0 ELSE tank2 = CINT((LOG(tank2) * 1.442695) - 12)
         IF tank(tank1) > 0 AND tank(tank2) > 0 THEN del = .06 ELSE del = .12
         IF tank1 > 0 THEN tank(tank1) = tank(tank1) - (del * (1 + (health%(i, 3) / 4)))
         IF tank2 > 0 THEN tank(tank2) = tank(tank2) - (del * (1 + (health%(i, 3) / 4)))
3       NEXT i
        FOR i = 0 TO 12
         IF tank(i) > 100 THEN tank(i) = 100
         IF tank(i) < 0 THEN tank(i) = 0
        NEXT i
        'GOTO 9
9       GOSUB 1300
        GOSUB 3900
        GOSUB 1500

       
        'check door open/closed status from parallel port
        '------------------------------------------------
        'GOTO 97
        OUT 890, 204
        zt = TIMER
191     IF TIMER - zt < .001 THEN 191
        V = INP(889)
        IF V AND 16 THEN d(1) = 4 ELSE d(1) = 3
        IF V AND 32 THEN d(2) = 4 ELSE d(2) = 3
        IF V AND 64 THEN d(4) = 4 ELSE d(4) = 3
        IF V AND 128 THEN d(3) = 3 ELSE d(3) = 4
        OUT 890, 206
        zt = TIMER
192     IF TIMER - zt < .001 THEN 192
        V = INP(889)
        IF V AND 16 THEN d(5) = 4 ELSE d(5) = 3
        IF V AND 32 THEN d(6) = 4 ELSE d(6) = 3
        IF V AND 64 THEN d(8) = 4 ELSE d(8) = 3
        IF V AND 128 THEN d(7) = 3 ELSE d(7) = 4
        FOR i = 1 TO 8
         if dw(i)=3 then d(i) = 3
         if dw(i)=4 then d(i) = 4
        NEXT i
        '------------------------------------------------
       
        'obtain error codes
        '------------------
97      GOSUB 99
        '------------------

        'obtain simulation time and check for restart code
        '------------------
117     OPEN "R", #1, "time.rnd", 26
        inpSTR$=space$(26)
        Get #1, 1, inpSTR$
        close #1
        if inpSTR$="A"+space$(24)+"A" then 150
        OLDyear=year
        OLDday=day
        OLDhr=hr
        OLDmin=min
        OLDsec=sec
        IF mid$(inpSTR$,2,5) = "XXXXX" THEN RUN "gas3v"
        if len(inpSTR$)<>26 then 118
        if left$(inpSTR$,1)<>right$(inpSTR$,1) then 118
        year=cvi(mid$(inpSTR$,2,2))
        day=cvi(mid$(inpSTR$,4,2))
        hr=cvi(mid$(inpSTR$,6,2))
        min=cvi(mid$(inpSTR$,8,2))
        sec=cvd(mid$(inpSTR$,10,8))
118     timeFLAG=2
        if year<>OLDyear then timeFLAG=0
        if day<>OLDday then timeFLAG=0
        if hr<>OLDhr then timeFLAG=0
        if min<>OLDmin then timeFLAG=0
        if sec<>OLDsec then timeFLAG=0
        COLOR 10+timeFLAG, 0
        LOCATE 25, 1: PRINT using "###";day;:print ":";:print using "##";hr;:print ":";:print using "##";min;:print ":";:print using "##";sec;
        '-----------------                                    
       
        'emergency conditions
        '--------------------
150     FOR i = 1 TO 6
         IF FIRE(i) < 5 THEN delT = TEMP(i) - (298 + (100 * FIRE(i)))
         delTadjust = .1 * (101 - ch(i, 0)) / 101
         IF delTadjust < .001 THEN delTadjust = .001 / (1 + (.1 * ABS(delTadjust)))
         IF ABS(delT) > 1 THEN TEMP(i) = TEMP(i) - (delT * delTadjust)
         purgevalve = 0
         IF ch(i, 18) <= 0 THEN 152
           n(i, 1) = n(i, 1) + (.7852 * 10 * ch(i, 18))
           n(i, 2) = n(i, 2) + (.1926 * 10 * ch(i, 18))
           n(i, 4) = n(i, 4) + (.0096 * 10 * ch(i, 18))
           n(i, 5) = n(i, 5) + (.0123 * 10 * ch(i, 18))
152      IF i = 5 AND purge = 1 THEN purgevalve = 1: GOTO 151
         IF ch(i, 18) >= 0 THEN 153
151      c1 = i
         c2 = 0
         opening = ABS(ch(i, 18)) + purgevalve
         GOSUB 8000
153      n(i, 2) = n(i, 2) + ch(i, 19)
         n(i, 3) = n(i, 3) + ch(i, 20)
         n(i, 5) = n(i, 5) + ch(i, 21)
         n(i, 6) = n(i, 6) + (ch(i, 22) / 10)
         n(i, 7) = n(i, 7) + (ch(i, 23) * 10)
         n(i, 8) = n(i, 8) + (ch(i, 24) * 10)
         IF FIRE(i) < 5 THEN n(i, 2) = n(i, 2) - (FIRE(i) * .05)
         IF FIRE(i) < 5 THEN n(i, 3) = n(i, 3) + (FIRE(i) * .05)
         IF FIRE(i) < 5 THEN n(i, 5) = n(i, 5) + (FIRE(i) * .05)
         IF FIRE(i) < 5 THEN n(i, 6) = n(i, 6) + (FIRE(i) * .015)
         IF FIRE(i) < 5 THEN n(i, 7) = n(i, 7) + (FIRE(i) * 2)
        NEXT i
        FOR i = 1 TO 6
         ch(i, 0) = 0
         FOR j = 1 TO 6
          ch(i, j) = (n(i, j) * 8.31 * (TEMP(i)) / ch(i, 9))
          ch(i, 0) = ch(i, 0) + ch(i, j)
         NEXT j
         FOR j = 1 TO 6
          ch(i, j) = ch(i, j) / ch(i, 0)
         NEXT j
         '**ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i
        '--------------------

        'H20 CO2 Scrubbers and dust filters
        '----------------------------------
        FOR i = 1 TO 6
         IF ch(i, 14) = -1 AND ch(i, 3) > 0 THEN n(i, 3) = n(i, 3) - .01
         IF ch(i, 14) = 1 AND ch(i, 3) < 10 THEN n(i, 3) = n(i, 3) + .01
         IF ch(i, 15) = -1 AND ch(1, 5) > 0 THEN n(i, 5) = n(i, 5) - .01
         IF ch(i, 15) = 1 AND ch(i, 5) < 10 THEN n(i, 5) = n(i, 5) + .01
         IF ch(i, 16) = -1 AND n(i, 7) > 10 THEN n(i, 7) = n(i, 7) - 10
        NEXT i
        '----------------------------------
       
        'gas exchange through open doors
        '-------------------------------
        FOR i = 1 TO 7
         IF d(i) = 3 THEN 103
         c1 = dr(i, 4)
         c2 = dr(i, 5)
         opening = 1.5
         GOSUB 8000
103     NEXT i
        '-------------------------------


        'venting and pressurizing pumps
        '------------------------------
        FOR i = 1 TO 6
         IF ch(i, 11) = 0 THEN 101
         IF ch(i, 11) < 0 THEN 102
        
         'pressurize
         '----------
104      IF ch(i, 0) > 100000 THEN 101
         IF ch(i, 17) = 0 THEN 109
         IF ch(i, 0) > 98 THEN ch(i, 11) = .05 ELSE ch(i, 11) = 1
         'IF i = 5 AND ch(i, 11) = 1 THEN ch(i, 11) = .05
         IF ch(i, 0) > 101.3 THEN ch(i, 17) = 0: ch(i, 11) = 0: GOTO 101
109      nN2 = (.7852 * 10 * ch(i, 11))
         nO2g = (.1926 * 10 * ch(i, 11))
         nAr = (.0096 * 10 * ch(i, 11))
         nCO2 = (.0003 * 10 * ch(i, 11))
         nH2O = (.0123 * 10 * ch(i, 11))
         IF GT(3, 0) > 0 AND GT(3, 1) = 1 THEN n(i, 1) = n(i, 1) + nN2: GT(3, 0) = GT(3, 0) - (nN2 * .05): nN2 = 0
         IF GT(4, 0) > 0 AND GT(4, 1) = 1 THEN n(i, 1) = n(i, 1) + nN2: GT(4, 0) = GT(4, 0) - (nN2 * .05)
         IF GT(1, 0) > 0 AND GT(1, 1) = 1 THEN n(i, 2) = n(i, 2) + nO2g: GT(1, 0) = GT(1, 0) - (nO2g * .25): nO2g = 0
         IF GT(2, 0) > 0 AND GT(2, 1) = 1 THEN n(i, 2) = n(i, 2) + nO2g: GT(2, 0) = GT(2, 0) - (nO2g * .25)
         IF GT(5, 0) > 0 AND GT(5, 1) = 1 THEN n(i, 3) = n(i, 3) + nCO2: GT(5, 0) = GT(5, 0) - (nCO2 * 1)
         IF GT(6, 0) > 0 AND GT(6, 1) = 1 THEN n(i, 4) = n(i, 4) + nAr: GT(6, 0) = GT(6, 0) - (nAr * 1)
         IF GT(7, 0) - (water * 1.56) > 0 AND GT(7, 1) = 1 THEN n(i, 5) = n(i, 5) + nH2O: GT(7, 0) = GT(7, 0) - (nH2O * .5)
        
         ch(i, 10) = n(i, 1) + n(i, 2) + n(i, 3) + n(i, 4) + n(i, 5) + n(i, 6)
         ch(i, 0) = ch(i, 10) * TEMP(i) * 8.31 / ch(i, 9)
         GOTO 101

         'vent
         '----
102      IF ch(i, 17) = -1 AND ch(i, 0) <= 0 THEN ch(i, 17) = 0: ch(i, 11) = 0: GOTO 101
         IF ch(i, 11) < -2 AND ch(i, 0) < 150 THEN ch(i, 11) = -2
         IF i = 6 AND ch(i, 0) > 155 THEN ch(i, 11) = -5
         IF i = 6 AND ch(i, 0) > 750 THEN ch(i, 11) = -30
         IF i = 6 AND ch(i, 0) > 7500 THEN ch(i, 11) = -300
         oldP = ch(i, 0)
         oldN = ch(i, 10)
         IF GT(8, 1) = 1 AND ch(i, 10) > 0 THEN GT(8, 0) = GT(8, 0) - (.1 * ch(i, 11) * ventFACTOR)
         ch(i, 10) = ch(i, 10) + (10 * ch(i, 11) * ventFACTOR)
         'IF ch(i, 0) < .0001 THEN ch(i, 0) = .0001
         ch(i, 0) = ch(i, 10) * 8.31 * TEMP(i) / ch(i, 9)
         IF ch(i, 0) < .0001 THEN ch(i, 0) = .0001
         FOR j = 1 TO 8
          n(i, j) = n(i, j) * ch(i, 0) / oldP
         NEXT j

101     NEXT i
        '------------------------------

        'Recalculate partial pressures
        '-----------------------------
        FOR i = 1 TO 6
         FOR j = 1 TO 6
          IF n(i, j) < 0 THEN n(i, j) = 0
          ch(i, j) = (n(i, j) * 8.31 * (TEMP(i)) / ch(i, 9)) / ch(i, 0)
         NEXT j
         '**IF n(i, 6) < 0 THEN n(i, 6) = 0
         IF n(i, 7) < 0 THEN n(i, 7) = 0
         IF n(i, 8) < 0 THEN n(i, 8) = 0
         '**ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i
        '-----------------------------
        GOSUB 3900


        'warnings
        '--------
        warnFLAG = 0
        FOR i = 1 TO 6
         c(i) = 0
         IF ch(i, 0) < 97 THEN c(i) = 1
         IF ch(i, 0) > 110 THEN c(i) = 1
         IF ch(i, 3) * ch(i, 0) > .5 THEN c(i) = 1
         IF ch(i, 3) * ch(i, 0) < .005 THEN c(i) = 1
         IF ch(i, 5) * ch(i, 0) > 5 THEN c(i) = 1
         IF ch(i, 5) * ch(i, 0) < .5 THEN c(i) = 1
         IF ch(i, 2) * ch(i, 0) < 18 THEN c(i) = 1
         IF ch(i, 2) * ch(i, 0) > 50 THEN c(i) = 1
         IF ch(i, 6) > .0004 THEN c(i) = 1
         IF ch(i, 7) > .05 THEN c(i) = 1
         IF ch(i, 8) > .001 THEN c(i) = 1

         IF ch(i, 6) > .005 THEN c(i) = 2
         IF ch(i, 7) > .1 THEN c(i) = 2
         IF ch(i, 8) > .01 THEN c(i) = 2
         IF ch(i, 2) * ch(i, 0) < 15 THEN c(i) = 2
         IF ch(i, 2) * ch(i, 0) > 99 THEN c(i) = 2
         IF ch(i, 3) * ch(i, 0) < .002 THEN c(i) = 2
         IF ch(i, 3) * ch(i, 0) > 5 THEN c(i) = 2
         IF ch(i, 0) > 120 THEN c(i) = 2
         IF ch(i, 0) < 85 THEN c(i) = 2
         IF c(i) = 2 AND warnFLAG + alarmSILENCE = 0 THEN GOSUB 5000
         IF c(i) = 2 THEN warnFLAG = 1
         IF c(i) = 1 AND warnFLAG + alarmSILENCE = 0 THEN GOSUB 5010
         IF c(i) = 1 THEN warnFLAG = 1
        NEXT i
        IF warnFLAG = 0 THEN alarmSILENCE = 0
        '--------

        'send door warning status to parallel port
        '-----------------------------------------
        doorWARNbyte = 0
        FOR i = 1 TO 8
         IF ABS(ch(dr(i, 1), 0) - ch(dr(i, 2), 0)) > 10 THEN doorWARNbyte = doorWARNbyte + (2 ^ (i - 1))
        NEXT i
        'OUT 888, doorWARNbyte
        '-----------------------------------------
       
       
        'retrieve user inputs from mission control program
        '-------------------------------------------------
170     k=1
171     OPEN "R", #1, "GASMC.RND", 82
        inpSTR$=space$(82)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 82 then 120
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 172
        k=k+1
        if k<5 then 171 else fileINwarn=1:goto 120

172     k=2
        for i=1 to 6
          zz=cvi(mid$(inpSTR$,k,2)):k=k+2
          if zz>-9 then ch(i,11)=zz
          zz=cvi(mid$(inpSTR$,k,2)):k=k+2
          if zz>-9 then ch(i,14)=zz
          zz=cvi(mid$(inpSTR$,k,2)):k=k+2
          if zz>-9 then ch(i,15)=zz
          zz=cvi(mid$(inpSTR$,k,2)):k=k+2
          if zz>-9 then ch(i,16)=zz
        next i
        FOR i = 1 TO 8
         zz=cvi(mid$(inpSTR$,k,2)): k=k+2
         'IF zz <> -10 THEN d(i) = zz
        NEXT i
        GOTO 120
        '-------------------------------------------------


        'user input
        '----------
111     z$ = INKEY$
        IF z$ = "" THEN 112
        IF z$ = CHR$(27) THEN END
        IF z$ = CHR$(13) THEN alarmSILENCE = 1
        IF z$ = CHR$(0) + "P" THEN cmp = cmp + 1: IF cmp = 7 THEN cmp = 1
        IF z$ = CHR$(0) + "H" THEN cmp = cmp - 1: IF cmp = 0 THEN cmp = 6
        IF z$ = CHR$(0) + "M" THEN door = door + 1: IF door = 9 THEN door = 1
        IF z$ = CHR$(0) + "K" THEN door = door - 1: IF door = 0 THEN door = 8
        IF z$ = CHR$(9) THEN d(door) = d(door) + 1: IF d(door) = 5 THEN d(door) = 3
        if dw(door) = 3 then d(door) = 3
        if dw(door) = 4 then d(door) = 4
        IF UCASE$(z$) = "+" AND ch(cmp, 11) < 2 THEN ch(cmp, 11) = ch(cmp, 11) + 1
        IF UCASE$(z$) = "-" AND ch(cmp, 11) > -2 THEN ch(cmp, 11) = ch(cmp, 11) - 1
        IF z$ = CHR$(0) + ";" THEN IF ch(cmp, 14) = 0 THEN ch(cmp, 14) = -1 ELSE ch(cmp, 14) = 0
        IF z$ = CHR$(0) + "<" THEN IF ch(cmp, 14) = 0 THEN ch(cmp, 14) = 1 ELSE ch(cmp, 14) = 0
        IF z$ = CHR$(0) + "=" THEN IF ch(cmp, 15) = 0 THEN ch(cmp, 15) = -1 ELSE ch(cmp, 15) = 0
        IF z$ = CHR$(0) + ">" THEN IF ch(cmp, 15) = 0 THEN ch(cmp, 15) = 1 ELSE ch(cmp, 15) = 0
        IF z$ = CHR$(0) + "?" THEN IF ch(cmp, 16) = 0 THEN ch(cmp, 16) = -1 ELSE ch(cmp, 16) = 0
        IF z$ = CHR$(0) + CHR$(133) THEN IF ch(cmp, 17) = 0 THEN ch(cmp, 17) = -1: ch(cmp, 11) = -1 ELSE ch(cmp, 17) = 0: ch(cmp, 11) = 0
        IF z$ = CHR$(0) + CHR$(134) THEN IF ch(cmp, 17) = 0 THEN ch(cmp, 17) = 1: ch(cmp, 11) = 1 ELSE ch(cmp, 17) = 0: ch(cmp, 11) = 0
        IF z$ = "$" THEN purge = 1 - purge
        IF z$ = "x" THEN decom = 60
        IF z$ = CHR$(0) + "I" THEN ASTRO = ASTRO - 1: IF ASTRO = 0 THEN ASTRO = ASTROtotal
        IF z$ = CHR$(0) + "Q" THEN ASTRO = ASTRO + 1: IF ASTRO > ASTROtotal THEN ASTRO = 1
        IF z$ = CHR$(0) + "R" THEN IF (ASTROstat(ASTRO) AND 1) = 0 THEN ASTROstat(ASTRO) = ASTROstat(ASTRO) + 1 ELSE ASTROstat(ASTRO) = ASTROstat(ASTRO) - 1
        IF z$ = CHR$(0) + "S" THEN IF (ASTROstat(ASTRO + 8) AND 1) = 0 THEN ASTROstat(ASTRO + 8) = ASTROstat(ASTRO + 8) + 1 ELSE ASTROstat(ASTRO + 8) = ASTROstat(ASTRO + 8) - 1
        IF (ASTROstat(ASTRO + 8) AND 1) = 1 AND (ASTROstat(ASTRO) AND 2097150) = 0 THEN ASTROstat(ASTRO + 8) = ASTROstat(ASTRO + 8) - 1
        IF z$ = CHR$(0) + "G" THEN tnk = tnk - 1: IF tnk < .9 THEN tnk = 12
        IF z$ = CHR$(0) + "O" THEN tnk = tnk + 1: IF tnk > 12.1 THEN tnk = 1
        IF UCASE$(z$) = "Y" AND tankRC(1) <> 0 THEN tankRC(1) = 0: z$ = ""
        IF UCASE$(z$) = "Z" AND tankRC(2) <> 0 THEN tankRC(2) = 0: z$ = ""
        IF UCASE$(z$) = "Y" THEN GOSUB 1400
        IF UCASE$(z$) = "Z" THEN GOSUB 1400
        IF z$ = "/" AND tankRC(1) <> tnk AND tankRC(2) <> tnk THEN GOSUB 1200
        IF z$ = "*" AND tankRC(1) <> tnk AND tankRC(2) <> tnk THEN GOSUB 1200

        IF z$ = "a" THEN IF (ASTROstat(9) AND 1) = 0 THEN ASTROstat(9) = ASTROstat(9) + 1 ELSE ASTROstat(9) = ASTROstat(9) - 1
        IF z$ = "b" THEN IF (ASTROstat(10) AND 1) = 0 THEN ASTROstat(10) = ASTROstat(10) + 1 ELSE ASTROstat(10) = ASTROstat(10) - 1
        IF z$ = "c" THEN IF (ASTROstat(11) AND 1) = 0 THEN ASTROstat(11) = ASTROstat(11) + 1 ELSE ASTROstat(11) = ASTROstat(11) - 1
        IF z$ = "d" THEN IF (ASTROstat(12) AND 1) = 0 THEN ASTROstat(12) = ASTROstat(12) + 1 ELSE ASTROstat(12) = ASTROstat(12) - 1
        IF z$ = "e" THEN IF (ASTROstat(13) AND 1) = 0 THEN ASTROstat(13) = ASTROstat(13) + 1 ELSE ASTROstat(13) = ASTROstat(13) - 1
        IF z$ = "f" THEN IF (ASTROstat(14) AND 1) = 0 THEN ASTROstat(14) = ASTROstat(14) + 1 ELSE ASTROstat(14) = ASTROstat(14) - 1
        IF z$ = "g" THEN IF (ASTROstat(15) AND 1) = 0 THEN ASTROstat(15) = ASTROstat(15) + 1 ELSE ASTROstat(15) = ASTROstat(15) - 1
        IF z$ = "h" THEN IF (ASTROstat(16) AND 1) = 0 THEN ASTROstat(16) = ASTROstat(16) + 1 ELSE ASTROstat(16) = ASTROstat(16) - 1
        '                               
        IF z$ = "A" THEN IF (ASTROstat(1) AND 1) = 0 THEN ASTROstat(1) = ASTROstat(1) + 1 ELSE ASTROstat(1) = ASTROstat(1) - 1
        IF z$ = "B" THEN IF (ASTROstat(2) AND 1) = 0 THEN ASTROstat(2) = ASTROstat(2) + 1 ELSE ASTROstat(2) = ASTROstat(2) - 1
        IF z$ = "C" THEN IF (ASTROstat(3) AND 1) = 0 THEN ASTROstat(3) = ASTROstat(3) + 1 ELSE ASTROstat(3) = ASTROstat(3) - 1
        IF z$ = "D" THEN IF (ASTROstat(4) AND 1) = 0 THEN ASTROstat(4) = ASTROstat(4) + 1 ELSE ASTROstat(4) = ASTROstat(4) - 1
        IF z$ = "E" THEN IF (ASTROstat(5) AND 1) = 0 THEN ASTROstat(5) = ASTROstat(5) + 1 ELSE ASTROstat(5) = ASTROstat(5) - 1
        IF z$ = "F" THEN IF (ASTROstat(6) AND 1) = 0 THEN ASTROstat(6) = ASTROstat(6) + 1 ELSE ASTROstat(6) = ASTROstat(6) - 1
        IF z$ = "G" THEN IF (ASTROstat(7) AND 1) = 0 THEN ASTROstat(7) = ASTROstat(7) + 1 ELSE ASTROstat(7) = ASTROstat(7) - 1
        IF z$ = "H" THEN IF (ASTROstat(8) AND 1) = 0 THEN ASTROstat(8) = ASTROstat(8) + 1 ELSE ASTROstat(8) = ASTROstat(8) - 1
        IF z$ = "2" AND PR(1) > 0 THEN PR(1) = PR(1) - 1: probelaunch = 10: probe = 1
        IF z$ = "3" AND PR(2) > 0 THEN PR(2) = PR(2) - 1: probelaunch = 10: probe = 2
        IF z$ = "4" AND PR(3) > 0 THEN PR(3) = PR(3) - 1: probelaunch = 10: probe = 3
        IF z$ = "5" AND PR(4) > 0 THEN PR(4) = PR(4) - 1: probelaunch = 10: probe = 4
        IF z$ = "6" THEN probelaunch = -2: probe = 0
        IF z$ = "[" AND packblock = 0 THEN pack = pack - 1: IF pack = 0 THEN pack = 5
        IF z$ = "]" AND packblock = 0 THEN pack = pack + 1: IF pack = 6 THEN pack = 1

        IF z$ = "j" AND GT(1, 1) <> 2 THEN GT(1, 1) = 1 - GT(1, 1)
        IF z$ = "k" AND GT(2, 1) <> 2 THEN GT(2, 1) = 1 - GT(2, 1)
        IF z$ = "l" AND GT(3, 1) <> 2 THEN GT(3, 1) = 1 - GT(3, 1)
        IF z$ = "m" AND GT(4, 1) <> 2 THEN GT(4, 1) = 1 - GT(4, 1)
        IF z$ = "n" AND GT(5, 1) <> 2 THEN GT(5, 1) = 1 - GT(5, 1)
        IF z$ = "o" AND GT(6, 1) <> 2 THEN GT(6, 1) = 1 - GT(6, 1)
        IF z$ = "p" AND GT(7, 1) <> 2 THEN GT(7, 1) = 1 - GT(7, 1)
        IF z$ = "q" AND GT(8, 1) <> 2 THEN GT(8, 1) = 1 - GT(8, 1)

        IF z$ = "J" AND GT(1, 1) <> 1 THEN GT(1, 1) = 2 - GT(1, 1)
        IF z$ = "K" AND GT(2, 1) <> 1 THEN GT(2, 1) = 2 - GT(2, 1)
        IF z$ = "L" AND GT(3, 1) <> 1 THEN GT(3, 1) = 2 - GT(3, 1)
        IF z$ = "M" AND GT(4, 1) <> 1 THEN GT(4, 1) = 2 - GT(4, 1)
        'IF z$ = "N" AND GT(5, 1) <> 1 THEN GT(5, 1) = 2 - GT(5, 1)
        'IF z$ = "O" AND GT(6, 1) <> 1 THEN GT(6, 1) = 2 - GT(6, 1)
        'IF z$ = "P" AND GT(7, 1) <> 1 THEN GT(7, 1) = 2 - GT(7, 1)
        IF z$ = "Q" AND GT(8, 1) <> 1 THEN GT(8, 1) = 2 - GT(8, 1)
        IF z$ = "v" THEN rechargeENABLE = 1 - rechargeENABLE
        'IF rechargeBLOCK = 1 THEN rechargeENABLE = 0
        IF z$ = "w" AND CO2purge < 1 THEN CO2purge = 300
        
        IF z$ = "\" THEN BP1 = BP1 + 1
        IF BP1 > 7 THEN BP1 = 0
        'IF z$ = "*" THEN MAGshield = MAGshield + .01
        'IF z$ = "/" THEN MAGshield = MAGshield - .01
        'IF MAGshield < 0 THEN MAGshield = 0
        '----------
        'cls
        'for i=1 to 8:print d(i):next i
        'z$=input$(1)


        'print warning indications
        '-------------------------
120     'LOCATE 22, 1: PRINT purge;
        LOCATE 1, 72
        IF Asteroid = 0 THEN COLOR 8, 0: PRINT "ASTEROID";
        IF Asteroid = 1 THEN COLOR 14, 0: PRINT "ASTEROID";
        IF Asteroid = 2 THEN COLOR 12, 0: PRINT "ASTEROID";
        LOCATE 2, 44: COLOR 9, 0: PRINT "Wind: "; : COLOR 14, 0: PRINT USING "####"; WIND * 3.6; : COLOR 9, 0: PRINT " km/h";
        LOCATE 1, 61
        IF discharge = 1 THEN BEEP: lightningK = 10
        IF lightningK > 0 THEN lightningK = lightningK - .5
        Efield = CINT(lightning - lightningK)
        IF Efield < 0 THEN Efield = 0
        IF Efield = 0 THEN COLOR 8, 0
        IF Efield = 1 THEN COLOR 9, 0
        IF Efield = 2 THEN COLOR 11, 0
        IF Efield = 3 THEN COLOR 14, 0
        IF Efield = 4 THEN COLOR 13, 0
        IF Efield = 5 THEN COLOR 12, 0
        PRINT "EL FIELD ";
        LOCATE 2, 61
        COLOR 8 + (discharge * 6), 0
        PRINT "DISCHARGE";
        FOR i = 1 TO 8
         IF door = i THEN doorCLR = 1 ELSE doorCLR = 0
         COLOR 9, doorCLR
         LOCATE 12 + i, 1: PRINT USING "#"; i;
         IF d(i) = 4 THEN COLOR 14, doorCLR: PRINT " OPEN ";
         IF d(i) = 3 THEN COLOR 10, doorCLR: PRINT " SHUT ";
         IF de(i) = 10 THEN COLOR 12, doorCLR ELSE COLOR 10, doorCLR
         IF de(i) = 10 THEN PRINT "MF ";  ELSE PRINT "OK ";
         IF ABS(ch(dr(i, 1), 0) - ch(dr(i, 2), 0)) > 10 THEN COLOR 12, doorCLR ELSE COLOR 10, doorCLR
         PRINT "PRESS";
        NEXT i

        COLOR 9, 0
        LOCATE 1, 17: PRINT "RAD OUT:";
        COLOR 14, 0
        PRINT USING "#####.######"; RAD * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
        COLOR 9, 0
        LOCATE 2, 17: PRINT "     IN: ";
        COLOR 14, 0
        PRINT USING "####.######"; RADin * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
        COLOR 9, 0
        LOCATE 1, 45: PRINT "OAT:";
        COLOR 14, 0
        PRINT USING "#####"; OAT - 273 + (3 * (DELtemp - 7)); : COLOR 9, 0: PRINT " "; CHR$(248); "C";
        COLOR 7, 0
       
        IF flare > 0 THEN COLOR 12, 0 ELSE COLOR 8, 0
        LOCATE 2, 72: PRINT "FLARE/CME";

        warnCC = warnCC + 12: IF warnCC = 24 THEN warnCC = 0
        LOCATE 22, 2: COLOR warnCC, 0: IF warn = 1 THEN PRINT "WARNING";  ELSE PRINT "       ";

        ventFACTOR = (250 - ch(0, 0)) / 250
        IF GT(8, 1) = 1 THEN ventFACTOR = (100 - GT(8, 0)) / 100
        IF ventFACTOR < 0 THEN ventFACTOR = 0
        ventFACTOR = SQR(ventFACTOR)
        GOSUB 1300
        COLOR 7, 0
        GOSUB 200
        '-------------------------

  
112     IF TIMER - ttt > .5 THEN 190
        GOTO 111

        'write status variables to telemetry output file
        '-----------------------------------------------
190     chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$=chr$(chkBYTE+64)
        FOR i = 0 TO 6
         FOR j = 1 TO 8
          outSTR$=outSTR$+MKS$(n(i, j))
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         dd = d(i)
         IF de(i) = 10 THEN dd = dd + 10
         outSTR$=outSTR$+mki$(dd)
        NEXT i
        outSTR$=outSTR$+mki$(Asteroid)
        outSTR$=outSTR$+mki$(WIND)
        outSTR$=outSTR$+mki$(dustX)
        outSTR$=outSTR$+mki$(lightning)
        outSTR$=outSTR$+mki$(DELtemp)
        outSTR$=outSTR$+mks$(recharge)
        outSTR$=outSTR$+mks$(atm)
        outSTR$=outSTR$+mks$(OAT)
        outSTR$=outSTR$+mks$(discharge)
        outSTR$=outSTR$+mks$(water)
        outSTR$=outSTR$+mks$(packblock)
        outSTR$=outSTR$+mks$(flareQ)
        outSTR$=outSTR$+mks$(flare)
        outSTR$=outSTR$+mks$(rechargeBLOCK)
        outSTR$=outSTR$+mks$(warn)
        outSTR$=outSTR$+mks$(delATM)
        outSTR$=outSTR$+mks$(location)
        FOR i = 1 TO 6
         outSTR$=outSTR$+mks$(ch(i, 29))
        NEXT i
        probelaunchsignal=0
        IF probelaunch > 2 THEN probelaunchsignal = -10: probelaunch = probelaunch - 1
        IF probelaunch < 0 THEN probelaunchsignal = -20: probelaunch = 0
        outSTR$=outSTR$+mks$(probelaunchsignal)
        outSTR$=outSTR$+mks$(decom)
        outSTR$=outSTR$+mks$(RAD)
        outSTR$=outSTR$+mks$(RADin)
        outSTR$=outSTR$+mki$(pack)
        outSTR$=outSTR$+mki$(probe)
        FOR i = 1 TO 8
         outSTR$=outSTR$+mks$(ASTROrad(i))
        NEXT i
        FOR i = 1 TO 6
         outSTR$=outSTR$+mki$(FIRE(i))
         outSTR$=outSTR$+mki$(TEMP(i))
        NEXT i
        FOR i = 1 TO 8
         outSTR$=outSTR$+mks$(GT(i, 0))
         outSTR$=outSTR$+mks$(GT(i, 1))
         outSTR$=outSTR$+mks$(ASTROstat(i))
         outSTR$=outSTR$+mks$(ASTROstat(i + 8))
        NEXT i
        'locate 1,1:print using "##.##"; GT(8,0);cvs(mid$(outstr$,512,4));
        FOR i = 1 TO 10
         outSTR$=outSTR$+mks$(tankRC(i))
        NEXT i
        FOR i = 1 TO 12
         outSTR$=outSTR$+mks$(tank(i))
        NEXT i
        FOR i = 0 TO 8
         FOR j = 1 TO 7
          outSTR$=outSTR$+mki$(health%(i, j))
         NEXT j
        NEXT i
        outSTR$=outSTR$+flaresource$
        outSTR$=outSTR$+warning1$
        outSTR$=outSTR$+warning2$
        outSTR$=outSTR$+chr$(chkBYTE+64)
        'cls
        'print len(outSTR$)
        'print len(flaresource$)
        'print len(warning1$)
        'print len(warning2$)
        'z$=input$(1)
        'end
        open "R", #1, "gastelemetry.rnd",800
        put #1, 1, outSTR$
        close #1
        GOTO 1
        '-----------------------------------------------




        'print primary graphical data to screen
        '--------------------------------------
200     IF ch(5, 0) > 1 THEN decom = 0
        IF decom > 0 THEN decom = decom - 1
        LOCATE 25, 60
        COLOR 11, 0
        IF decom > 40 THEN PRINT "VAC  ";
        IF ABS(decom - 30) < 11 THEN PRINT "WSrad";
        IF decom < 20 THEN PRINT "mist ";
        IF decom < 1 THEN LOCATE 25, 60: PRINT "decon";
        IF decom > 0 THEN LOCATE 25, 65: PRINT USING "###"; decom;  ELSE LOCATE 25, 65: PRINT "   ";
        IF decom > 1 THEN c(5) = 5
       
        FOR i = 1 TO 7
         FOR j = da(i, 11) TO da(i, 12)
          FOR k = da(i, 13) TO da(i, 14)
           IF i < 7 THEN ii = i ELSE ii = 2
           IF cmp = ii THEN chrt = 219 ELSE chrt = 177
           COLOR a(c(ii)), 0
           LOCATE k, j: PRINT CHR$(chrt);
          NEXT k
         NEXT j
        NEXT i
       
        FOR i = 1 TO 8
         IF de(i) = 10 THEN drbk = 4 ELSE drbk = 0
         IF ABS(ch(dr(i, 1), 0) - ch(dr(i, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 10
         IF door = i AND de(i) <> 10 THEN drbk = 3
         IF door = i AND de(i) = 10 THEN drbk = 5
         COLOR drfg, drbk
         FOR j = 1 TO 15 STEP 14
          LOCATE da(i, j + 1), da(i, j)
          PRINT CHR$(da(i, d(i)));
         NEXT j
        NEXT i
        COLOR 7, 0
        LOCATE 2, 15: IF purge = 0 THEN PRINT CHR$(179);  ELSE PRINT CHR$(216);

       
       
        '--------------------------------------
       
        'write primary gas data to screen
        '--------------------------------
        COLOR 9, 0
        LOCATE 3, 20: PRINT "   Press     N2      O2     CO2     Ar   H2O  chem dust  bio";
        COLOR 7, 0
        tempDISPflag = 1 - tempDISPflag
        FOR i = 0 TO 6
         IF i = 0 THEN 210
         LOCATE 3 + ch(i, 13), ch(i, 12)
         COLOR 7, 0
         IF ch(i, 11) < -1 THEN PRINT "V";
         IF ch(i, 11) = -1 THEN PRINT "v";
         IF ch(i, 11) = 1 THEN PRINT "p";
         IF ch(i, 11) = 2 THEN PRINT "P";
         LOCATE 4 + i, 16
         COLOR 7 + (5 * SGN(INT(ABS((FIRE(i) - .5))))), 0
         IF TEMP(i) < 1272 THEN PRINT USING "###_ "; TEMP(i) - 273;  ELSE PRINT "999";
         IF tempDISPflag * SGN(INT(FIRE(i) - .5)) > 0 THEN LOCATE 4 + i, 16: PRINT "FIRE";
         IF cmp = i THEN COLOR 10 + (2 * SGN(INT(ABS((FIRE(i) - .5))))), 1 ELSE COLOR 7 + (5 * SGN(INT(ABS((FIRE(i) - .5))))), 0
210      LOCATE 4 + i, 20
         IF i = 0 THEN PRINT "AM";  ELSE PRINT using "#";i;:print " ";
         Xval = ch(i, 0): IF Xval > 999900 THEN Xval = 999900
         IF Xval > 999.9 THEN PRINT USING "###.#_k_ "; Xval / 1000;  ELSE PRINT USING "###.##_ "; Xval;
         Xval = ch(i, 1) * ch(i, 0): IF Xval > 999990 THEN Xval = 999990
         IF Xval > 999.99 THEN PRINT USING "###.##_k_ "; Xval / 1000;  ELSE PRINT USING "###.##_ _ "; Xval;
         Xval = ch(i, 2) * ch(i, 0): IF Xval > 999990 THEN Xval = 999990
         IF Xval > 999.99 THEN PRINT USING "###.##_k_ "; Xval / 1000;  ELSE PRINT USING "###.##_ _ "; Xval;
         Xval = ch(i, 3) * ch(i, 0): IF Xval > 999990 THEN Xval = 999990
         IF Xval > 999.99 THEN PRINT USING "###.##_k_ "; Xval / 1000;  ELSE PRINT USING "###.##_ _ "; Xval;
         Xval = ch(i, 4) * ch(i, 0): IF Xval > 99990 THEN Xval = 99990
         IF Xval > 99.99 THEN PRINT USING "##.##_k"; Xval / 1000;  ELSE PRINT USING "##.##_ "; Xval;
         Xval = ch(i, 5) * ch(i, 0): IF Xval > 99990 THEN Xval = 99990
         IF Xval > 99.99 THEN PRINT USING "##.##_k"; Xval / 1000;  ELSE PRINT USING "##.##_ "; Xval;
         Xval = ch(i, 6) * ch(i, 0): IF Xval > 99990 THEN Xval = 99990
         IF Xval > 99.99 THEN PRINT USING "##.##_k"; Xval / 1000;  ELSE PRINT USING "##.##_ "; Xval;
         IF i = 0 THEN dstX = dustX ELSE dstX = 0
         Xval = ch(i, 7) + dstX: IF Xval > 99.9 THEN Xval = 99.9
         IF Xval < .999 THEN PRINT USING ".###_ "; Xval;  ELSE PRINT USING "##.#_ "; Xval;
         Xval = ch(i, 8): IF Xval > 99.9 THEN Xval = 99.9
         IF Xval < .999 THEN PRINT USING ".###"; Xval;  ELSE PRINT USING "##.#"; Xval;
        NEXT i
        
        COLOR 9, 0
        LOCATE 12, 57: PRINT "AUXILIARY GAS SYSTEMS  ";
        LOCATE 13, 57: PRINT " CO2   H2O   DUST  Press";
        LOCATE 20, 57: PRINT "F1/F2 F3/F4  F5  F11/F12";
        FOR i = 1 TO 6
         LOCATE 13 + i, 57
         IF cmp = i THEN COLOR 10, 1 ELSE COLOR 10, 0
         IF ch(i, 14) = -1 THEN PRINT "SCRUB ";
         IF ch(i, 14) = 0 THEN PRINT "      ";
         IF ch(i, 14) = 1 THEN PRINT " ADD  ";
         IF ch(i, 15) = -1 THEN PRINT "SCRUB ";
         IF ch(i, 15) = 0 THEN PRINT "      ";
         IF ch(i, 15) = 1 THEN PRINT " ADD  ";
         IF ch(i, 16) = 0 THEN PRINT "      ";
         IF ch(i, 16) = -1 THEN PRINT "FILTER";
         IF ch(i, 17) = -1 THEN PRINT " AUTO-";
         IF ch(i, 17) = 0 THEN PRINT "      ";
         IF ch(i, 17) = 1 THEN PRINT " AUTO+";
        NEXT i
        COLOR 7, 0
        RETURN
        '--------------------------------


        'Load air tanks into astro back packs
1200    FOR j = 1 TO 8
         tank11 = (ASTROstat(j) AND 8190)
         tank12 = (ASTROstat(j) AND 33546240)
         IF tank11 < 1 THEN tank1 = 0 ELSE tank1 = LOG(tank11) * 1.442695
         IF tank12 < 1 THEN tank2 = 0 ELSE tank2 = (LOG(tank12) * 1.442695) - 12
         tank1 = CINT(tank1)
         tank2 = CINT(tank2)
         IF tank1 = tnk AND j <> ASTRO THEN RETURN
         IF tank2 = tnk AND j <> ASTRO THEN RETURN
         IF z$ = "/" AND tank2 = tnk THEN RETURN
         IF z$ = "*" AND tank1 = tnk THEN RETURN
         IF tnk = tankRC(1) THEN RETURN
         IF tnk = tankRC(2) THEN RETURN
        NEXT j
        tank11 = (ASTROstat(ASTRO) AND 8190)
        tank12 = (ASTROstat(ASTRO) AND 33546240)
        IF z$ = "/" AND tank11 <> 0 THEN ASTROstat(ASTRO) = ASTROstat(ASTRO) - tank11: RETURN
        IF z$ = "*" AND tank12 <> 0 THEN ASTROstat(ASTRO) = ASTROstat(ASTRO) - tank12: RETURN
        tank13 = 2 ^ tnk
        IF z$ = "*" THEN tank13 = 2 ^ (tnk + 12)
        ASTROstat(ASTRO) = ASTROstat(ASTRO) + tank13
        RETURN

1300    FOR i = 1 TO 8
         IF GT(i, 0) < 0 THEN GT(i, 0) = 0
        NEXT i
        ON BP1 + 1 GOSUB 7000, 7100, 7000, 7200, 7000, 7300, 7000, 7400
        IF BP1 / 2 = INT(BP1 / 2) THEN BP1 = BP1 + 1
        COLOR 9, 0
        LOCATE 11, 31: PRINT "H P R O T S";
        FOR i = 1 TO ASTROtotal
         IF ASTRO = i THEN bkclr = 1 ELSE bkclr = 0
         COLOR 9, bkclr
         LOCATE 11 + i, 18: PRINT CHR$(64 + i);
         IF (ASTROstat(i) AND 1) = 0 THEN COLOR 10, bkclr: PRINT "I";  ELSE COLOR 14, bkclr: PRINT "O";
         IF ASTROrad(i) > 200 THEN fgclr = 14 ELSE fgclr = 10
         IF ASTROrad(i) > 10000 THEN fgclr = 12
         COLOR fgclr, bkclr:
         PRINT USING "####.###"; ASTROrad(i) * 1000;
         COLOR 9, bkclr: PRINT "mS";
         z = (ASTROstat(i + 8) AND 1)
         
         FOR j = 1 TO ASTROtotal
          fgclr = 10
          IF ABS(health%(i, j)) = 3 THEN fgclr = 12
          IF ABS(health%(i, j)) = 2 THEN fgclr = 14
          zz = 2
          IF health%(i, j) < 0 THEN zz = 22
          IF health%(i, j) > 0 THEN zz = 43
          IF health%(i, j) = -4 THEN fgclr = 11: zz = 25
          IF health%(i, j) = -5 THEN fgclr = 3: zz = 25
          IF health%(i, j) = -6 THEN fgclr = 9: zz = 25
          IF health%(i, j) = -7 THEN fgclr = 1: zz = 72

          COLOR fgclr, bkclr:
          PRINT " "; CHR$(zz);
         NEXT j
         PRINT " ";
         tank1 = (ASTROstat(i) AND 8190)
         tank2 = (ASTROstat(i) AND 33546240)
         IF tank1 < 1 THEN tank1 = 0 ELSE tank1 = CINT(LOG(tank1) * 1.442695)
         IF tank2 < 1 THEN tank2 = 0 ELSE tank2 = CINT((LOG(tank2) * 1.442695) - 12)
         IF tank1 = 0 THEN PRINT SPACE$(6); : GOTO 1313
         COLOR 9 + (z * 2), bkclr: PRINT USING "##"; tank1; : PRINT ":";
         IF tank(tank1) < 30 THEN COLOR 14, bkclr ELSE COLOR 10, bkclr
         IF tank(tank1) < 10 THEN COLOR 12, bkclr
         PRINT USING "###"; tank(tank1);
1313     IF tank2 = 0 THEN PRINT SPACE$(7); : GOTO 1314
         COLOR 9 + (z * 2), bkclr: PRINT USING "###"; tank2; : PRINT ":";
         IF tank(tank2) < 30 THEN COLOR 14, bkclr ELSE COLOR 10, bkclr
         IF tank(tank2) < 10 THEN COLOR 12, bkclr
         PRINT USING "###"; tank(tank2);
1314     NEXT i
         RETURN


1400    FOR i = 1 TO 8
         tank1 = (ASTROstat(i) AND 8190)
         tank2 = (ASTROstat(i) AND 33546240)
         IF tank1 < 1 THEN tank1 = 0 ELSE tank1 = LOG(tank1) * 1.442695
         IF tank2 < 1 THEN tank2 = 0 ELSE tank2 = (LOG(tank2) * 1.442695) - 12
         tank1 = CINT(tank1)
         tank2 = CINT(tank2)
         IF tank1 = tnk THEN RETURN
         IF tank2 = tnk THEN RETURN
        NEXT i
        IF UCASE$(z$) = "Y" AND tankRC(2) = tnk THEN RETURN
        IF UCASE$(z$) = "Z" AND tankRC(1) = tnk THEN RETURN
        IF UCASE$(z$) = "Y" THEN tankRC(1) = tnk
        IF UCASE$(z$) = "Z" THEN tankRC(2) = tnk
        RETURN


1500    FOR i = 1 TO 6
         nO2(i) = 0
        NEXT i
        FOR i = 1 TO ASTROtotal
         IF (ASTROstat(i + 8) AND 1) = 1 THEN 1501
         IF (ASTROstat(i) AND 1) = 0 THEN nO2(health%(i, 7)) = nO2(health%(i, 7)) + (.000143 * (1 + (health%(i, 3) / 4)))
1501    NEXT i
        
        FOR i = 1 TO ASTROtotal
         nO2RM = 1
         tank1 = 1: IF GT(1, 0) = 0 OR GT(1, 1) <> 1 THEN tank1 = 0
         tank2 = 1: IF GT(2, 0) = 0 OR GT(2, 1) <> 1 THEN tank2 = 0
         IF tank1 = 0 AND tank2 = 0 THEN nO2RM = 0
         IF tank1 = 1 AND tank2 = 1 THEN nO2RM = .5
         IF GT(1, 0) * GT(1, 1) > 0 THEN GT(1, 0) = GT(1, 0) - (.25 * nO2(i) * nO2RM)
         IF GT(2, 0) * GT(2, 1) > 0 THEN GT(2, 0) = GT(2, 0) - (.25 * nO2(i) * nO2RM)
         IF nO2RM = 0 THEN n(i, 2) = n(i, 2) - (nO2(i))
         IF nO2(i) > .0006 THEN n(i, 3) = n(i, 3) + (nO2(i) - .0006): n(i, 5) = n(i, 5) + (nO2(i) - .0006)
         IF nO2(i) > .0006 THEN delW = .0006 ELSE delW = nO2(i)
         IF GT(7, 0) - (1.56 * water) > 99.99 THEN delW = 0
         IF GT(7, 1) <> 1 THEN delW = 0
         GT(7, 0) = GT(7, 0) + delW
        NEXT i

        IF GT(7, 1) = 1 THEN GT(7, 0) = GT(7, 0) + (IS2 * .0003)
        IF GT(1, 0) > 0 AND GT(1, 1) = 1 THEN GT(1, 0) = GT(1, 0) - (IS2 * .0003): IS2 = 0
        IF GT(2, 0) > 0 AND GT(2, 1) = 1 THEN GT(2, 0) = GT(2, 0) - (IS2 * .0003)
        
        recharge = 0
        IF rechargeENABLE = 0 THEN 1510
        FOR j = 1 TO 4
         if GT(j, 1) = 2 then recharge = recharge + 1
         IF GT(j, 1) = 2 AND GT(j, 0) < 100 THEN GT(j, 0) = GT(j, 0) + .05
        NEXT j

1510    FOR j = 1 TO 8
         IF GT(j, 0) > 100 THEN GT(j, 0) = 100
         IF GT(j, 0) < 0 THEN GT(j, 0) = 0
        NEXT j
       
        IF GT(8, 1) = 2 THEN GT(8, 0) = GT(8, 0) - ventFACTOR
        IF GT(8, 0) < 0 THEN GT(8, 0) = 0
        IF CO2purge > 0 THEN CO2purge = CO2purge - 1
        IF CO2purge < 1 THEN CO2purge = 0
        RETURN
         



        'error trapping routine
        '----------------------
2000    CLS
        e = ERR
        PRINT "line="; ERL
        PRINT "error="; e
        z$ = INPUT$(1)
        END
        '----------------------

        'calculation of external ambient partial pressures
        '-------------------------------------------------
3900    'Generic Partial Pressures
        'locate 19,29:print atm;P(location,0);
        'atm=0.8485
        IF atm > P(location, 0) THEN atm = P(location, 0)
        IF atm <= 0 THEN OAT = .01 ELSE OAT = .01 + (P(location, 1) * (atm / P(location, 0))^.3)
        'oat=260
        ch(0, 9) = 100000000
3901    ch(0, 0) = (atm / P(location, 2)) * 8.31 * OAT * delATM
        ch(0, 1) = chBASE(location, 1)
        ch(0, 2) = chBASE(location, 2)
        ch(0, 3) = chBASE(location, 3)
        ch(0, 4) = chBASE(location, 4)
        ch(0, 5) = chBASE(location, 5)
        ch(0, 6) = chBASE(location, 6)
3902    ch(0, 7) = chBASE(location, 7) * (atm / P(location, 0))
3903    ch(0, 8) = chBASE(location, 8) * (atm / P(location, 0))
3094    ch(0, 10) = ch(0, 0) * ch(0, 9) / ((OAT) * 8.31)
        FOR j = 1 TO 6
         n(0, j) = ch(0, j) * ch(0, 10)
        NEXT j
        n(0, 7) = ch(0, 7) * ch(0, 9)
        n(0, 8) = ch(0, 8) * ch(0, 9)
        'locate 19,19:print ch(0,0);
        RETURN



5000    'SOUND 300, 1
        'FOR i = 1 TO 4: LOCATE 22, 40 + i: PRINT "*"; : NEXT i
        't = TIMER
5001    'IF TIMER - t < .1 THEN 5001
        'FOR i = 1 TO 4: LOCATE 22, 40 + i: PRINT " "; : NEXT i
        RETURN

5010    'SOUND 200, 1
        'FOR i = 1 TO 4: LOCATE 22, 40 + i: PRINT "#"; : NEXT i
        't = TIMER
5011    'IF TIMER - t < .1 THEN 5011
        'FOR i = 1 TO 4: LOCATE 22, 40 + i: PRINT " "; : NEXT i
        RETURN


6000    filename$ = "EECOMRS.rnd": GOTO 6020
6010    filename$ = "GASTELEMetry.rnd"
6020    k=1
6021    inpSTR$=space$(800)
        open "R", #1, filename$, 800
        get #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 6030
        k=k+1
        if k<3 then 6021 else 6099
        
6030    k=2
        FOR i = 0 TO 6
         FOR j = 1 TO 8
           n(i,j)=CVS(mid$(inpSTR$,k,4))
           k=k+4
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         d(i)=CVi(mid$(inpSTR$,k,2))
         IF d(i) = 13 THEN d(i) = 3
         IF d(i) = 14 THEN d(i) = 4
         k=k+2
        NEXT i
        Asteroid = CVI(mid$(inpSTR$,k,2)):k=k+2
        WIND  = CVI(mid$(inpSTR$,k,2)):k=k+2
        dustX = CVI(mid$(inpSTR$,k,2)):k=k+2
        lightning = CVI(mid$(inpSTR$,k,2)):k=k+2
        DELtemp = CVI(mid$(inpSTR$,k,2)):k=k+2
        rechargeENABLE = sgn(CVS(mid$(inpSTR$,k,4))):k=k+4
        atm = CVS(mid$(inpSTR$,k,4)):k=k+4
        OAT = CVS(mid$(inpSTR$,k,4)):k=k+4
        discharge = CVS(mid$(inpSTR$,k,4)):k=k+4
        water = CVS(mid$(inpSTR$,k,4)):k=k+4
        packblock = CVS(mid$(inpSTR$,k,4)):k=k+4
        flareQ = CVS(mid$(inpSTR$,k,4)):k=k+4
        flare = CVS(mid$(inpSTR$,k,4)):k=k+4
        rechargeBLOCK = CVS(mid$(inpSTR$,k,4)):k=k+4
        warn = CVS(mid$(inpSTR$,k,4)):k=k+4
        delATM = CVS(mid$(inpSTR$,k,4)):k=k+4
        location = CVS(mid$(inpSTR$,k,4)):k=k+4
        FOR i = 1 TO 6
         ch(i,29) = CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        k=k+4
        decom = CVS(mid$(inpSTR$,k,4)):k=k+4
        RAD = CVS(mid$(inpSTR$,k,4)):k=k+4
        RADin = CVS(mid$(inpSTR$,k,4)):k=k+4
        pack = CVi(mid$(inpSTR$,k,2)):k=k+2
        probe = CVi(mid$(inpSTR$,k,2)):k=k+2
        FOR i = 1 TO 8
         ASTROrad(i)= CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 1 TO 6
         FIRE(i) = CVi(mid$(inpSTR$,k,2)):k=k+2
         TEMP(i) = CVi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        FOR i = 1 TO 8
         GT(i, 0) = CVS(mid$(inpSTR$,k,4)):k=k+4
         GT(i, 1)= CVS(mid$(inpSTR$,k,4)):k=k+4
         ASTROstat(i) = CVS(mid$(inpSTR$,k,4)):k=k+4
         ASTROstat(i+8) = CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 1 TO 10
         tankRC(i) = CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 1 TO 12
         tank(i) = CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 0 TO 8
         FOR j = 1 TO 7
          health%(i,j) = CVI(mid$(inpSTR$,k,4)):k=k+2
         NEXT j
        NEXT i
        flaresource$= mid$(inpSTR$,k,8):k=k+8
        warning1$= mid$(inpSTR$,k,25):k=k+25
        warning2$= mid$(inpSTR$,k,25):k=k+25
6099    RETURN


7000    FOR i = 20 TO 25
         LOCATE i, 18
         PRINT SPACE$(38);
        NEXT i
        RETURN

7100    LOCATE 20, 43
        COLOR 9, 0: PRINT "/:"; : COLOR 11, 0: PRINT "tk1";
        COLOR 9, 0: PRINT "  *:"; : COLOR 11, 0: PRINT "tk2";
        COLOR 9, 0
        LOCATE 22, 18: PRINT "Hm:";
        LOCATE 25, 18: PRINT "Ed:";
        FOR i = 1 TO 4
         FOR j = 1 TO 3
          'IF j = 3 THEN DELj = 1 ELSE DELj = 0
          LOCATE 21 + i, 15 + (j * 6) + DELj
          IF tnk = ((j - 1) * 4) + i THEN bkclr = 1 ELSE bkclr = 0
          COLOR 11, bkclr
          IF j < 3 THEN PRINT USING "#_:"; ((j - 1) * 4) + i;
          IF j = 3 THEN PRINT USING "##_:"; ((j - 1) * 4) + i;
          IF tank(((j - 1) * 4) + i) < 75 THEN fgclr = 14 ELSE fgclr = 10
          IF tank(((j - 1) * 4) + i) < 50 THEN fgclr = 12
          COLOR fgclr, bkclr
          PRINT USING "###"; tank(((j - 1) * 4) + i);
         NEXT j
        NEXT i
        COLOR 9, 0
        LOCATE 20, 18: PRINT "RECHARGE Y:";
        COLOR 11, 0
        PRINT USING "##_  "; tankRC(1);
        IF tank(tankRC(1)) < 75 THEN fgclr = 14 ELSE fgclr = 10
        IF tank(tankRC(1)) < 50 THEN fgclr = 12
        COLOR fgclr, 0
        PRINT USING "###"; tank(tankRC(1));
        COLOR 9, 0
        LOCATE 21, 18: PRINT "RECHARGE Z:";
        COLOR 11, 0
        PRINT USING "##_  "; tankRC(2);
        IF tank(tankRC(2)) < 75 THEN fgclr = 14 ELSE fgclr = 10
        IF tank(tankRC(2)) < 50 THEN fgclr = 12
        COLOR fgclr, 0
        PRINT USING "###"; tank(tankRC(2));

        LOCATE 21, 42
        COLOR 11, 0: PRINT "O2:";
        IF GT(1, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(1, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(1, 0);
        COLOR 11, 0: PRINT " O2:";
        IF GT(2, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(2, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(2, 0);
        LOCATE 22, 42
        COLOR 11, 0: PRINT "N2:";
        IF GT(3, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(3, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(3, 0);
        COLOR 11, 0: PRINT " N2:";
        IF GT(4, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(4, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(4, 0);
        LOCATE 23, 41
        COLOR 11, 0: PRINT "CO2:";
        IF GT(5, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(5, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(5, 0);
        COLOR 11, 0: PRINT " Ar:";
        IF GT(6, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(6, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(6, 0);
        LOCATE 24, 41
        COLOR 11, 0: PRINT "H2O:";
        IF GT(7, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(7, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###"; GT(7, 0) - (water * 1.56);
        LOCATE 25, 41
        COLOR 11, 0: PRINT "LPR:";
        IF GT(8, 0) > 50 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(8, 0) > 80 THEN COLOR 12, 0
        PRINT USING "###"; GT(8, 0);

        RETURN


7200   
        COLOR 9, 0
        LOCATE 20, 19: PRINT " PROBES             SCIENCE PACKS";
        LOCATE 21, 18: COLOR 9, 0: PRINT "2"; : COLOR 10, 0: PRINT "    pluto           ";
        IF pack = 1 THEN COLOR 10, 1 ELSE COLOR 10, 0
        PRINT "MAD         "; : COLOR 9, 0: PRINT "[";
        LOCATE 22, 18: COLOR 9, 0: PRINT "3"; : COLOR 10, 0: PRINT "    explosive       ";
        IF pack = 2 THEN COLOR 10, 1 ELSE COLOR 10, 0
        PRINT "weather     ";
        LOCATE 23, 18: COLOR 9, 0: PRINT "4"; : COLOR 10, 0: PRINT "    seismic         ";
        IF pack = 3 THEN COLOR 10, 1 ELSE COLOR 10, 0
        PRINT "gravity     ";
        LOCATE 24, 18: COLOR 9, 0: PRINT "5"; : COLOR 10, 0: PRINT "    grnd/atms samp  ";
        IF pack = 4 THEN COLOR 10, 1 ELSE COLOR 10, 0
        PRINT "particle    ";
        LOCATE 25, 18: COLOR 9, 0: PRINT "6"; : COLOR 10, 0: PRINT "    detonate probe  ";
        IF pack = 5 THEN COLOR 10, 1 ELSE COLOR 10, 0
        PRINT "passive EM  "; : COLOR 9, 0: PRINT "]";
        COLOR 14, 0
        LOCATE 21, 20: PRINT USING "##"; PR(1);
        LOCATE 22, 20: PRINT USING "##"; PR(2);
        LOCATE 23, 20: PRINT USING "##"; PR(3);
        LOCATE 24, 20: PRINT USING "##"; PR(4);
        RETURN


7300    IF warn = 0 THEN COLOR 10, 0 ELSE COLOR 12, 0
        LOCATE 21, 20: PRINT warning1$;
        LOCATE 22, 20: PRINT warning2$;
        IF flare = 0 THEN LOCATE 23, 20: COLOR 10, 0: PRINT "No Stellar Flare Activity"; : flareQ = 0
        IF flare > 0 THEN LOCATE 23, 20: COLOR 14, 0: PRINT flaresource$; : COLOR 12, 0: PRINT " flare activity    ";
        LOCATE 22, 47
        IF flareQ = 8 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 218
        PRINT CHR$(zzz);
        IF flareQ = 1 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 196
        PRINT CHR$(zzz);
        IF flareQ = 2 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 191
        PRINT CHR$(zzz);
        LOCATE 23, 47
        IF flareQ = 7 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 179
        PRINT CHR$(zzz);
        COLOR 10 + (2 * SGN(flare)), 0: PRINT USING "#"; flare;
        IF flareQ = 3 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 179
        PRINT CHR$(zzz);
        LOCATE 24, 47
        IF flareQ = 6 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 192
        PRINT CHR$(zzz);
        IF flareQ = 5 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 196
        PRINT CHR$(zzz);
        IF flareQ = 4 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 217
        PRINT CHR$(zzz);
        RETURN



7400    LOCATE 21, 20
        COLOR 11, 0: PRINT "O2 "; : COLOR 9, 0: PRINT "j:";
        IF GT(1, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(1, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(1, 0);
        COLOR 11, 0:
        IF GT(1, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(1, 1) = 1 THEN PRINT " SRC   ";
        IF GT(1, 1) = 2 THEN PRINT " RCHRG ";
        PRINT " O2 "; : COLOR 9, 0: PRINT "k:";
        IF GT(2, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(2, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(2, 0);
        COLOR 11, 0:
        IF GT(2, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(2, 1) = 1 THEN PRINT " SRC   ";
        IF GT(2, 1) = 2 THEN PRINT " RCHRG ";
        LOCATE 22, 20
        PRINT "N2 "; : COLOR 9, 0: PRINT "l:"; :
        IF GT(3, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(3, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(3, 0);
        COLOR 11, 0:
        IF GT(3, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(3, 1) = 1 THEN PRINT " SRC   ";
        IF GT(3, 1) = 2 THEN PRINT " RCHRG ";
        PRINT " N2 "; : COLOR 9, 0: PRINT "m:";
        IF GT(4, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(4, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(4, 0);
        COLOR 11, 0:
        IF GT(4, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(4, 1) = 1 THEN PRINT " SRC   ";
        IF GT(4, 1) = 2 THEN PRINT " RCHRG ";
        LOCATE 23, 19
        PRINT "CO2 "; : COLOR 9, 0: PRINT "n:"; :
        IF GT(5, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(5, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(5, 0);
        COLOR 11, 0:
        IF GT(5, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(5, 1) = 1 THEN PRINT " SRC   ";
        IF GT(5, 1) = 2 THEN PRINT " RCHRG ";
        PRINT " Ar "; : COLOR 9, 0: PRINT "o:";
        IF GT(6, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(6, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(6, 0);
        COLOR 11, 0:
        IF GT(6, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(6, 1) = 1 THEN PRINT " SRC   ";
        IF GT(6, 1) = 2 THEN PRINT " RCHRG ";
        LOCATE 24, 19
        PRINT "H2O "; : COLOR 9, 0: PRINT "p:"; :
        IF GT(7, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(7, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(7, 0) - (water * 1.56);
        COLOR 11, 0:
        IF GT(7, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(7, 1) = 1 THEN PRINT " SRC   ";
        IF GT(7, 1) = 2 THEN PRINT " RCHRG ";
        LOCATE 25, 19
        PRINT "LPR "; : COLOR 9, 0: PRINT "q:"; :
        IF GT(8, 0) > 50 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(8, 0) > 80 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(8, 0);
        COLOR 11, 0:
        IF GT(8, 1) = 0 THEN PRINT " ISOL  ";
        IF GT(8, 1) = 1 THEN PRINT " SRC   ";
        IF GT(8, 1) = 2 THEN PRINT " VENT  ";
        COLOR 9, 0: LOCATE 24, 42: PRINT "w: "; : COLOR 8 + (6 * SGN(CO2purge)), 0: PRINT "CO2 purge";
        COLOR 9, 0: LOCATE 25, 42: PRINT "v: "; : COLOR 8 + (6 * rechargeENABLE), 0: PRINT "RECHARGE";
        RETURN



'Gas Exchanges
8000    IF ch(c1, 9) > ch(c2, 9) THEN lowV = c2 ELSE lowV = c1
        FOR j = 1 TO 8
         delPt = SQR(ABS(ch(c1, 0) - ch(c2, 0)) / 101.3) + .01
         delP = ((ch(c1, j) * ch(c1, 0)) - (ch(c2, j) * ch(c2, 0))) * .5 * delPt * opening
         IF delP > 0 THEN highP = c1: lowP = c2 ELSE highP = c2: lowP = c1
         delP = ABS(delP)
         
8001     delN = delP * ch(lowV, 9) / (TEMP(lowV) * 8.31)
         IF highP > 0 THEN n(highP, j) = n(highP, j) - delN
         IF lowP > 0 THEN n(lowP, j) = n(lowP, j) + delN
         IF n(highP, j) < .00001 THEN n(highP, j) = .00001
         IF n(lowP, j) < .00001 THEN n(lowP, j) = .00001
        NEXT j
        
        IF c1 > 0 THEN ch(c1, 0) = 0
        IF c2 > 0 THEN ch(c2, 0) = 0
        FOR j = 1 TO 6
         IF n(c1, j) < 0 THEN n(c1, j) = 0
8002     IF c1 > 0 THEN ch(c1, j) = (n(c1, j) * 8.31 * (TEMP(c1)) / ch(c1, 9))
         IF c1 > 0 THEN ch(c1, 0) = ch(c1, 0) + ch(c1, j)
         IF n(c2, j) < 0 THEN n(c2, j) = 0
8003     IF c2 > 0 THEN ch(c2, j) = (n(c2, j) * 8.31 * (TEMP(c2)) / ch(c2, 9))
         IF c2 > 0 THEN ch(c2, 0) = ch(c2, 0) + ch(c2, j)
        NEXT j
        IF n(c1, 7) < 0 THEN n(c1, 7) = 0
        IF n(c1, 8) < 0 THEN n(c1, 8) = 0
8004    IF c1 > 0 THEN ch(c1, 7) = n(c1, 7) / ch(c1, 9)
8005    IF c1 > 0 THEN ch(c1, 8) = n(c1, 8) / ch(c1, 9)
        IF n(c2, 7) < 0 THEN n(c2, 7) = 0
        IF n(c2, 8) < 0 THEN n(c2, 8) = 0
8006    IF c2 > 0 THEN ch(c2, 7) = n(c2, 7) / ch(c2, 9)
8007    IF c2 > 0 THEN ch(c2, 8) = n(c1, 8) / ch(c2, 9)
       
        FOR j = 1 TO 6
8008     IF c1 > 0 THEN ch(c1, j) = ch(c1, j) / (ch(c1, 0) + .1)
8009     IF c2 > 0 THEN ch(c2, j) = ch(c2, j) / (ch(c2, 0) + .1)
        NEXT j
        ch(c1, 10) = 0
        ch(c2, 10) = 0
        FOR j = 1 TO 6
         ch(c1, 10) = ch(c1, 10) + n(c1, j)
         ch(c2, 10) = ch(c2, 10) + n(c2, j)
        NEXT j
       
8100    IF c1 = 0 THEN 8110
        FOR j = 1 TO 6
          IF n(c1, j) < 0 THEN n(c1, j) = 0
          ch(c1, j) = (n(c1, j) * 8.31 * (TEMP(c1)) / ch(c1, 9)) / ch(c1, 0)
        NEXT j
8110    IF c2 = 0 THEN 8120
        FOR j = 1 TO 6
          IF n(c2, j) < 0 THEN n(c2, j) = 0
          ch(c2, j) = (n(c2, j) * 8.31 * (TEMP(c2)) / ch(c2, 9)) / ch(c2, 0)
        NEXT j
8120    RETURN




        'input error codes
        '-----------------
99      k=1
719     open "R", #1, "gassim.rnd", 182
        inpSTR$=space$(182)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 182 then fileINwarn=1: goto 98
        
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 715
        k=k+1 
        if k<4 then 719 else 98

715     k=2
        FOR i = 1 TO 6
         ch(i, 18) = cvs(mid$(inpSTR$,k,4)):k=k+4            'holes in compartment
         ch(i, 19) = cvs(mid$(inpSTR$,k,4)):k=k+4            'oxygen variances
         ch(i, 20) = cvs(mid$(inpSTR$,k,4)):k=k+4            'carbon dioxide variance
         ch(i, 21) = cvs(mid$(inpSTR$,k,4)):k=k+4            'water variance
         ch(i, 22) = cvs(mid$(inpSTR$,k,4)):k=k+4            'chemical hazards variance
         ch(i, 23) = cvs(mid$(inpSTR$,k,4)):k=k+4            'dust variance
         ch(i, 24) = cvs(mid$(inpSTR$,k,4)):k=k+4            'biohazard variance
         Fire(i) = cvi(mid$(inpSTR$,k,4)):k=k+2
        NEXT i
        if chkCHAR1$ = chr$(64) then gosub 8200
        if chkCHAR2$ = chr$(123) then gosub 8250


98      k=1
717     OPEN "R", #1, "doorsim.rnd", 276
        inpSTR$=space$(276)
        GET #1, 1, inpSTR$
        close #1
        
        if len(inpSTR$) <> 276 then 711
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 718
        k=k+1 
        if k<4 then 717 else fileINwarn=1: goto 711

718     k=2
        for i=1 to 8
         dd=cvi(mid$(inpSTR$,k,2)):k=k+2
         if dd>9 then de(i)=10:dd=dd-10: else de(i)=0
         if cint(dd)=3 then dw(i)=3 else dw(i)=0
         if cint(dd)=4 then dw(i)=4
        next i
        lightning = cvi(mid$(inpSTR$,k,2)):k=k+2
        Asteroid = cvi(mid$(inpSTR$,k,2)):k=k+2
        WIND = cvi(mid$(inpSTR$,k,2)):k=k+2
        dustX = cvi(mid$(inpSTR$,k,2)):k=k+2
        DELtemp = cvi(mid$(inpSTR$,k,2)):k=k+2
        discharge = cvi(mid$(inpSTR$,k,2)):k=k+2
        water = cvi(mid$(inpSTR$,k,2)):k=k+2+2
        
        flareQ = cvi(mid$(inpSTR$,k,2)):k=k+2
        flare = cvi(mid$(inpSTR$,k,2)):k=k+2
        warn = cvi(mid$(inpSTR$,k,2)):k=k+2
        delATM = cvi(mid$(inpSTR$,k,2)):k=k+2
        delATM = (1+(delATM/315))
        
        atm = cvs(mid$(inpSTR$,k,4)):k=k+4
        RAD= cvs(mid$(inpSTR$,k,4)):k=k+4
        RADin= cvs(mid$(inpSTR$,k,4)):k=k+4
        FOR i = 1 TO 8
         ASTROrad(i)= cvs(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 1 TO 8
         FOR j = 1 TO 7
          health%(i, j) = cvi(mid$(inpSTR$,k,2)):k=k+2
         NEXT j
        NEXT i
        flaresource$ = mid$(inpSTR$,k,8):k=k+8
        warning1$ = mid$(inpSTR$,k,25):k=k+25
        warning2$ = mid$(inpSTR$,k,25):k=k+25+10
        location = cvi(mid$(inpSTR$,k,2)):k=k+2
        packblock = cvi(mid$(inpSTR$,k,2)):k=k+2
        rechargeBLOCK = cvi(mid$(inpSTR$,k,2)):k=k+2
        IS2 = cvs(mid$(inpSTR$,k,4))
711     RETURN


8250    for i = 1 to 7
         GT(i,0) = 100
        next i
        GT(8,0)=0
8200    FOR i = 1 TO 6
         TEMP(i) = 298
         ch(i, 0) = 101.3
         ch(i, 10) = ch(i, 0) * ch(i, 9) / (298 * 8.31)
         n(i, 1) = .7852 * ch(i, 10)
         n(i, 2) = .1926 * ch(i, 10)
         n(i, 3) = .0003 * ch(i, 10)
         n(i, 4) = .0096 * ch(i, 10)
         n(i, 5) = .0123 * ch(i, 10)
         n(i, 6) = 0
         n(i, 7) = 0
         n(i, 8) = 0
         for j=1 to 6
          ch(i, j) = (n(i, j) * 8.31 * (TEMP(i)) / ch(i, 9)) / ch(i, 0)
         next j
         ch(i,7)=0
         ch(i,8)=0
         'ch(i, 10) = 0
         'FOR j = 1 TO 6
         ' ch(i, 10) = ch(i, 10) + n(i, j)
         'NEXT j
         'ch(i, 0) = ch(i, 10) * (298 * 8.31) / ch(i, 9)
        NEXT i
        return
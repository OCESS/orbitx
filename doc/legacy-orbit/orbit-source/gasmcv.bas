        ON ERROR GOTO 2000
        DIM a(6), c(7), ch(7, 29), d(9), dr(10, 5), n(6, 10), dw(8), de(8), da(10, 16)
        DIM ASTROrad(8), ASTROstat(16), ASTROHstat(8, 1), health%(8, 7), tank(12), tankRC(10)
        DIM letter(44, 44, 2), Fire(6), Temp(6), GT(8, 1), probeNAME$(4), packNAME$(4)
        locate 1,1,0
        probeNAME$(0) = "        ": packNAME$(0) = "magnetic"
        probeNAME$(1) = "pluto   ": packNAME$(1) = "atms    "
        probeNAME$(2) = "explos  ": packNAME$(2) = "gravity "
        probeNAME$(3) = "seismic ": packNAME$(3) = "particle"
        probeNAME$(4) = "gen purp": packNAME$(4) = "pass EM "
        GOSUB 2200
        
        CLS
        color 7,0
        OPEN "I", #1, "eecomINI"
        INPUT #1, ASTROtotal
        FOR i = 0 TO 39
         INPUT #1, z, z, z
         FOR j = 1 TO 8
          INPUT #1, z
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
       
        cmp = 1
        pack = 1
        OPEN "R", #1, "EECOMMC.DAT"
        CLOSE #1
        OPEN "I", #1, "EECOMMC.DAT"
        IF EOF(1) THEN CLOSE #1: GOTO 11
        INPUT #1, pathname$
        CLOSE #1
11      transmit = 2
        bug = 164
        planet = 2
        HAB = 1

        'Compartment Gases
        ' 0=pressure
        ' 1=nitrogen
        ' 2=oxygen
        ' 3=carbon dioxide
        ' 4=argon
        ' 5=water
        ' 6=volatile chemicals
        ' 7=dust
        ' 8=biohazards
        ' 9=volume
        '10=contents
        '11=


        FOR i = 1 TO 6
         Temp(i) = 298
         ch(i, 10) = ch(i, 0) * ch(i, 9) / (298 * 8.31)
         FOR j = 1 TO 5
          n(i, j) = ch(i, j) * ch(i, 10)
         NEXT j
         n(i, 6) = ch(i, 6) * ch(i, 9)
         n(i, 7) = ch(i, 7) * ch(i, 9)
         n(i, 8) = ch(i, 8) * ch(i, 9)
        NEXT i
        door = 1
       

        'Recalculate partial pressures
        '-----------------------------
        FOR i = 0 TO 6
         ch(i, 0) = 0
         FOR j = 1 TO 6
          ch(i, j) = (n(i, j) * 8.31 * 298 / ch(i, 9))
          ch(i, 0) = ch(i, 0) + ch(i, j)
         NEXT j
         FOR j = 1 TO 6
          IF ch(i, 0) > 0 THEN ch(i, j) = ch(i, j) / ch(i, 0)
         NEXT j
         ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i
        '-----------------------------


1       ttt = TIMER
        
        FOR i = 1 TO 6
         FOR j = 23 TO 26
          ch(i, j) = -10
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         ch(7, i) = -10
        NEXT i

111     zz$ = INKEY$
        IF DISPLAYflag = 0 THEN GOSUB 300
        IF DISPLAYflag = 0 THEN GOSUB 200
        IF DISPLAYflag = 1 THEN GOSUB 400
        update = 0
        IF zz$ = "" THEN 112
        IF zz$ = CHR$(27) THEN END
        IF zz$ = CHR$(13) THEN CLS : DISPLAYflag = 1 - DISPLAYflag: IF DISPLAYflag = 1 THEN SCREEN 12: GOSUB 500 ELSE SCREEN 0: GOSUB 6100
       
        IF DISPLAYflag = 1 THEN 116
        IF zz$ = CHR$(0) + "P" THEN cmp = cmp + 1: IF cmp = 7 THEN cmp = 1
        IF zz$ = CHR$(0) + "H" THEN cmp = cmp - 1: IF cmp = 0 THEN cmp = 6
        IF zz$ = CHR$(0) + "M" THEN door = door + 1: IF door = 9 THEN door = 1
        IF zz$ = CHR$(0) + "K" THEN door = door - 1: IF door = 0 THEN door = 8
        IF UCASE$(zz$) = "+" AND ch(cmp, 11) < 2 THEN : transmit = 2:  ch(cmp, 11) = ch(cmp, 11) + 1: ch(cmp, 23) = ch(cmp, 11)
        IF UCASE$(zz$) = "-" AND ch(cmp, 11) > -2 THEN : transmit = 2:  ch(cmp, 11) = ch(cmp, 11) - 1: ch(cmp, 23) = ch(cmp, 11)
        IF zz$ = CHR$(0) + ";" THEN : transmit = 2:  IF ch(cmp, 14) = 0 THEN ch(cmp, 14) = -1: ch(cmp, 24) = -1 ELSE ch(cmp, 14) = 0: ch(cmp, 24) = 0
        IF zz$ = CHR$(0) + "<" THEN : transmit = 2:  IF ch(cmp, 14) = 0 THEN ch(cmp, 14) = 1: ch(cmp, 24) = 1 ELSE ch(cmp, 14) = 0: ch(cmp, 24) = 0
        IF zz$ = CHR$(0) + "=" THEN : transmit = 2:  IF ch(cmp, 15) = 0 THEN ch(cmp, 15) = -1: ch(cmp, 25) = -1 ELSE ch(cmp, 15) = 0: ch(cmp, 25) = 0
        IF zz$ = CHR$(0) + ">" THEN : transmit = 2:  IF ch(cmp, 15) = 0 THEN ch(cmp, 15) = 1: ch(cmp, 25) = 1 ELSE ch(cmp, 15) = 0: ch(cmp, 25) = 0
        IF zz$ = CHR$(0) + "?" THEN : transmit = 2:  IF ch(cmp, 16) = 0 THEN ch(cmp, 16) = -1: ch(cmp, 26) = -1 ELSE ch(cmp, 16) = 0: ch(cmp, 26) = 0
        IF zz$ = "A" THEN ASTROHstat(1, 0) = 1 - ASTROHstat(1, 0)
        IF zz$ = "B" THEN ASTROHstat(2, 0) = 1 - ASTROHstat(2, 0)
        IF zz$ = "C" THEN ASTROHstat(3, 0) = 1 - ASTROHstat(3, 0)
        IF zz$ = "D" THEN ASTROHstat(4, 0) = 1 - ASTROHstat(4, 0)
        IF zz$ = "E" THEN ASTROHstat(5, 0) = 1 - ASTROHstat(5, 0)
        IF zz$ = "F" THEN ASTROHstat(6, 0) = 1 - ASTROHstat(6, 0)
        GOSUB 300
        GOTO 112

116     IF zz$ = CHR$(0) + "P" THEN OLDbug = 0: planet = planet + 1: IF planet > 6 THEN planet = 0
        IF zz$ = CHR$(0) + "H" THEN OLDbug = 0: planet = planet - 1: IF planet < 0 THEN planet = 6
        IF zz$ = CHR$(0) + "M" THEN bug = bug + 1: IF bug > 632 THEN bug = 30
        IF zz$ = CHR$(0) + "K" THEN bug = bug - 1: IF bug < 30 THEN bug = 632
        IF UCASE$(zz$) = "S" THEN SUIT = 1 - SUIT
        IF UCASE$(zz$) = "H" THEN HAB = 1 - HAB
        IF UCASE$(zz$) = "A" THEN AYSE = 1 - AYSE
        IF UCASE$(zz$) = "M" THEN MAG = 1 - MAG
        IF UCASE$(zz$) = "D" THEN DISK = 1 - DISK
        
  
112     IF TIMER - ttt > 1 THEN 180
        GOTO 111

180     update = 1
        'IF transmit = 0
        FOR i = 1 TO 6
         IF ASTROHstat(i, 0) = 1 AND ASTROHstat(i, 1) > -7.1 THEN ASTROHstat(i, 1) = ASTROHstat(i, 1) - .05
         IF ASTROHstat(i, 0) = 0 AND ASTROHstat(i, 1) < 0 THEN ASTROHstat(i, 1) = ASTROHstat(i, 1) + .05
        NEXT i

        chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$=chr$(chkBYTE+64)
        FOR i = 1 TO 6
         FOR j = 23 TO 26
          outSTR$=outSTR$+mki$(ch(i, j))
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         outSTR$=outSTR$+mki$(-10)
        NEXT i
        FOR i = 1 TO 8
         IF ASTROHstat(i, 1) > -.1 THEN hibernation = 0 else hibernation = CINT(ASTROHstat(i, 1))
         outSTR$=outSTR$+mki$(hibernation)
        NEXT i
        outSTR$=outSTR$+chr$(chkBYTE+64)
        OPEN "R", #1, pathname$ + "GASMC.RND",82
        put #1, 1, outSTR$
        CLOSE #1

        IF transmit = 1 THEN transmit = 0
        IF transmit = 2 THEN transmit = 1
        IF transmit > 0 THEN 190
        FOR i = 1 TO 6
         ch(i, 11) = 0
         ch(i, 23) = -10
         FOR j = 24 TO 26
          ch(i, j) = -10
          'ch(i, j - 10) = 0
         NEXT j
        NEXT i

190     
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
        if OLDchkCHAR$=chkCHAR1$ then telemERROR = 4 else telemERROR = 0
        OLDchkCHAR$=chkCHAR1$
        FOR i = 0 TO 6
         FOR j = 1 TO 8
           n(i,j)=CVS(mid$(inpSTR$,k,4))
           k=k+4
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         d(i)=CVi(mid$(inpSTR$,k,2))
         IF d(i) = 13 THEN d(i) = 4
         IF d(i) = 14 THEN d(i) = 4
         k=k+2
        NEXT i
        Asteroid = CVI(mid$(inpSTR$,k,2)):k=k+2
        WIND  = CVI(mid$(inpSTR$,k,2)):k=k+2
        dustX = CVI(mid$(inpSTR$,k,2)):k=k+2
        lightning = CVI(mid$(inpSTR$,k,2)):k=k+2
        DELtemp = CVI(mid$(inpSTR$,k,2)):k=k+2
        rechargeENABLE = SGN(CVS(mid$(inpSTR$,k,4))):k=k+4
        atm = CVS(mid$(inpSTR$,k,4)):k=k+4
        OAT = CVS(mid$(inpSTR$,k,4)):k=k+4
        Temp(0)=OAT
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

       
6099    OPEN "R", #1, "time.rnd", 26
        inpSTR$=space$(26)
        Get #1, 1, inpSTR$
        OLDyear=year
        OLDday=day
        OLDhr=hr
        OLDmin=min
        OLDsec=sec
        IF mid$(inpSTR$,2,5) <> "XXXXX" THEN 6098
        inpSTR$="A"+space$(24)+"A"
        put #1, 1, inpSTR$
        close #1
        RUN "gasmcv"
        
6098    close #1
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
        IF DISPLAYflag = 1 THEN 192
        COLOR 10+timeFLAG, 0
        LOCATE 25, 1: PRINT using "###";day;:print ":";:print using "##";hr;:print ":";:print using "##";min;:print ":";:print using "##";sec;




        'Recalculate partial pressures
        '-----------------------------
192      FOR i = 0 TO 6
         ch(i, 0) = 0
         FOR j = 1 TO 6
          ch(i, j) = (n(i, j) * 8.31 * Temp(i) / ch(i, 9))
          ch(i, 0) = ch(i, 0) + ch(i, j)
         NEXT j
         FOR j = 1 TO 6
          IF ch(i, 0) > 0 THEN ch(i, j) = ch(i, j) / ch(i, 0)
         NEXT j
         'ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i
        '-----------------------------

        'warnings
        '--------
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
         IF ch(i, 2) * ch(i, 0) < 16 THEN c(i) = 2
         IF ch(i, 2) * ch(i, 0) > 99 THEN c(i) = 2
         IF ch(i, 3) * ch(i, 0) < .002 THEN c(i) = 2
         IF ch(i, 3) * ch(i, 0) > 1 THEN c(i) = 2
         IF ch(i, 0) > 120 THEN c(i) = 2
         IF ch(i, 0) < 85 THEN c(i) = 2
        NEXT i
        '--------
        GOTO 1



        'Primary Display
200     IF Decom > 0 THEN c(5) = 5
      
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
      
      
       
        COLOR 9, 0
        LOCATE 3, 20: PRINT "   Press     N2      O2     CO2     Ar   H2O  chem  dust bio";
        COLOR 7, 0
        FOR i = 0 TO 6
         IF i = 0 THEN 210
         LOCATE 3 + ch(i, 13), ch(i, 12)
         COLOR 7, 0
         IF ch(i, 11) < -1 THEN PRINT "V";
         IF ch(i, 11) > -2 AND ch(i, 11) < 0 THEN PRINT "v";
         IF ch(i, 11) > 0 AND ch(i, 11) < 2 THEN PRINT "p";
         IF ch(i, 11) = 2 THEN PRINT "P";

         LOCATE 4 + i, 16
         COLOR 7 + (5 * SGN(INT(ABS((Fire(i) - .5))))), 0
         IF Temp(i) < 1272 THEN PRINT USING "###_ "; Temp(i) - 273;  ELSE PRINT "999";
         IF tempDISPflag * SGN(INT(Fire(i) - .5)) > 0 THEN LOCATE 4 + i, 16: PRINT "FIRE";
         IF cmp = i THEN COLOR 10 + (2 * SGN(INT(ABS((Fire(i) - .5))))), 1 ELSE COLOR 7 + (5 * SGN(INT(ABS((Fire(i) - .5))))), 0


         IF cmp = i THEN COLOR 7, 1 ELSE COLOR 7, 0
210      LOCATE 4 + i, 20
         IF i = 0 THEN PRINT "AM";  ELSE PRINT using "#"; i;:print " ";
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

         'IF ch(i, 0) > 999.9 THEN PRINT USING "###.#_k_ "; ch(i, 0) / 1000;  ELSE PRINT USING "###.##_ "; ch(i, 0);
         'IF ch(i, 1) * ch(i, 0) > 999.99 THEN PRINT USING "###.##_k_ "; ch(i, 1) * ch(i, 0) / 1000;  ELSE PRINT USING "###.##_ _ "; ch(i, 1) * ch(i, 0);
         'IF ch(i, 2) * ch(i, 0) > 999.99 THEN PRINT USING "###.##_k_ "; ch(i, 2) * ch(i, 0) / 1000;  ELSE PRINT USING "###.##_ _ "; ch(i, 2) * ch(i, 0);
         'IF ch(i, 3) * ch(i, 0) > 999.99 THEN PRINT USING "###.##_k_ "; ch(i, 3) * ch(i, 0) / 1000;  ELSE PRINT USING "###.##_ _ "; ch(i, 3) * ch(i, 0);
         'PRINT USING "##.##_ "; ch(i, 4) * ch(i, 0);
         'PRINT USING "##.##_ "; ch(i, 5) * ch(i, 0);
         'IF ch(i, 6) < .009999 THEN PRINT USING ".####_ "; ch(i, 6) * 100;  ELSE PRINT USING "###.#_ "; ch(i, 6) * 100;
         'IF i = 0 THEN dstX = dustX ELSE dstX = 0
         'IF ch(i, 7) + dstX < .999 THEN PRINT USING ".###_ "; ch(i, 7) + dstX;  ELSE PRINT USING "##.#_ "; ch(i, 7) + dstX;
         'IF ch(i, 8) < .999 THEN PRINT USING ".###"; ch(i, 8);  ELSE PRINT USING "##.#"; ch(i, 8);
        NEXT i

        COLOR 9, 0
        LOCATE 12, 57: PRINT "AUXILIARY GAS SYSTEMS";
        LOCATE 13, 57: PRINT "  CO2    H2O   DUST ";
        LOCATE 20, 57: PRINT " F1/F2  F3/F4   F5  ";
        FOR i = 1 TO 6
         COLOR 7, 0
         LOCATE 13 + i, 57
         PRINT USING "#"; i;
         COLOR 10, 0
         IF ch(i, 14) = -1 THEN PRINT " SCRUB ";
         IF ch(i, 14) = 0 THEN PRINT "       ";
         IF ch(i, 14) = 1 THEN PRINT " ADD   ";
         IF ch(i, 15) = -1 THEN PRINT " SCRUB ";
         IF ch(i, 15) = 0 THEN PRINT "       ";
         IF ch(i, 15) = 1 THEN PRINT " ADD   ";
         IF ch(i, 16) = 0 THEN PRINT "       ";
         IF ch(i, 16) = -1 THEN PRINT "FILTER ";
        NEXT i
        COLOR 7, 0
        RETURN


300 
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
        PRINT USING "#####"; OAT - 273 + (3 * (DELtemp - 7)); : COLOR 9, 0: PRINT " "; CHR$(167); "C";
        COLOR 7, 0
     
        IF flare > 0 THEN COLOR 12, 0 ELSE COLOR 8, 0
        LOCATE 2, 72: PRINT "FLARE/CME";
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
        PRINT "ELC FIELD";
        LOCATE 2, 61
        COLOR 8 + (discharge * 6), 0
        PRINT "LIGHTNING";
        locate 25,13
        color 8+telemERROR,0
        print "TLM";

        'LOCATE 23, 20
        'IF Asteroid = 0 THEN COLOR 10, 0: PRINT "NO ASTEROIDS DETECTED     ";
        'IF Asteroid = 1 THEN COLOR 14, 0: PRINT "ASTEROID DETECTED         ";
        'IF Asteroid = 2 THEN COLOR 12, 0: PRINT "ASTEROID COLLISION WARNING";
        'LOCATE 2, 45: COLOR 9, 0: PRINT "Wind:  "; : COLOR 14, 0: PRINT USING "####"; WIND * 3.6; : COLOR 9, 0: PRINT " km/h";
        'LOCATE 2, 68
        'IF lightning = 0 THEN COLOR 8, 0
        'IF lightning = 1 THEN COLOR 9, 0
        'IF lightning = 2 THEN COLOR 14, 0
        'IF lightning = 3 THEN COLOR 12, 0
        'PRINT "LIGHTNING";
       
        COLOR 9, 0: LOCATE 13, 1: PRINT "D"; : PRINT USING "#"; door;
        IF d(door) = 4 THEN COLOR 14, 0: PRINT " O";
        IF d(door) = 3 THEN COLOR 10, 0: PRINT " S";
        IF de(door) = 10 THEN COLOR 12, 0 ELSE COLOR 10, 0
        PRINT " STAT";
        IF ABS(ch(dr(door, 1), 0) - ch(dr(door, 2), 0)) > 10 THEN COLOR 12, 0 ELSE COLOR 10, 0
        PRINT " PRESS";
        COLOR 9, 0: LOCATE 21, 58: PRINT CHR$(24); " "; CHR$(25); : COLOR 11, 0: PRINT "  select comp";
        COLOR 9, 0: LOCATE 22, 58: PRINT CHR$(17); " "; CHR$(16); : COLOR 11, 0: PRINT "  select door";
        COLOR 9, 0: LOCATE 24, 58: PRINT "A-H  "; : COLOR 11, 0: PRINT "astro hibernate";
        COLOR 9, 0: LOCATE 25, 58: PRINT "*:   "; : COLOR 11, 0: PRINT "hibernate enable";
        COLOR 9, 0: LOCATE 23, 58: PRINT "- +  "; : COLOR 11, 0: PRINT "press/vent";
        'COLOR 9, 0: LOCATE 2, 17: PRINT "OAT:"; : COLOR 14, 0: PRINT USING "#####"; OAT - 273 + (3 * (DELtemp - 7));
        'LOCATE 2, 39: COLOR 9, 0: PRINT "RAD SHIELD: "; : COLOR 14, 0: PRINT USING "#####"; MAGshield * 100;
        'COLOR 9, 0: LOCATE 1, 17: PRINT "RAD:"; : COLOR 14, 0: PRINT USING "#####.######"; RAD * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
        'COLOR 9, 0: PRINT "     INSIDE: "; : COLOR 14, 0: PRINT USING "#####.######"; RADin * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
       
        COLOR 9, 0
        LOCATE 12, 31: PRINT "H P R O T S";
        FOR i = 1 TO ASTROtotal
         IF ASTROHstat(i, 0) = 1 THEN bkclr = 5 ELSE bkclr = 0
         COLOR 9, bkclr
         LOCATE 12 + i, 18: PRINT CHR$(64 + i);
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
          IF tankRC(i + 2) = -4 THEN fgclr = 11: zz = 25
          IF tankRC(i + 2) = -5 THEN fgclr = 3: zz = 25
          IF tankRC(i + 2) = -6 THEN fgclr = 9: zz = 25
          IF tankRC(i + 2) = -7 THEN fgclr = 9: zz = 72

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
1314    NEXT i
      
        IF warn = 0 THEN COLOR 10, 0 ELSE COLOR 12, 0
        LOCATE 23, 18: PRINT warning1$;
        LOCATE 24, 18: PRINT warning2$;
        IF flare = 0 THEN LOCATE 25, 18: COLOR 10, 0: PRINT "No Stellar Flare Activity"; : flareQ = 0
        IF flare > 0 THEN LOCATE 25, 18: COLOR 14, 0: PRINT FLARESOURCE$; : COLOR 12, 0: PRINT " flare activity    ";
        LOCATE 23, 46
        IF flareQ = 8 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 218
        PRINT CHR$(zzz);
        IF flareQ = 1 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 196
        PRINT CHR$(zzz);
        IF flareQ = 2 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 191
        PRINT CHR$(zzz);
        LOCATE 24, 46
        IF flareQ = 7 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 179
        PRINT CHR$(zzz);
        COLOR 10 + (2 * SGN(flare)), 0: PRINT USING "#"; flare;
        IF flareQ = 3 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 179
        PRINT CHR$(zzz);
        LOCATE 25, 46
        IF flareQ = 6 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 192
        PRINT CHR$(zzz);
        IF flareQ = 5 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 196
        PRINT CHR$(zzz);
        IF flareQ = 4 THEN COLOR 12, 0: zzz = 254 ELSE COLOR 10, 0: zzz = 217
        PRINT CHR$(zzz);
       
        LOCATE 14, 1
        COLOR 11, 0
        PRINT "O2  ";
        IF GT(1, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(1, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(1, 0);
        COLOR 11, 0:
        IF GT(1, 1) = 0 THEN PRINT " ISOL";
        IF GT(1, 1) = 1 THEN PRINT " SRC ";
        IF GT(1, 1) = 2 THEN PRINT " RCHG";
        LOCATE 15, 1
        PRINT "O2  ";
        IF GT(2, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(2, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(2, 0);
        COLOR 11, 0:
        IF GT(2, 1) = 0 THEN PRINT " ISOL";
        IF GT(2, 1) = 1 THEN PRINT " SRC ";
        IF GT(2, 1) = 2 THEN PRINT " RCHG";
        LOCATE 16, 1
        PRINT "N2  ";
        IF GT(3, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(3, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(3, 0);
        COLOR 11, 0:
        IF GT(3, 1) = 0 THEN PRINT " ISOL";
        IF GT(3, 1) = 1 THEN PRINT " SRC ";
        IF GT(3, 1) = 2 THEN PRINT " RCHG";
        LOCATE 17, 1
        PRINT "N2  ";
        IF GT(4, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(4, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(4, 0);
        COLOR 11, 0:
        IF GT(4, 1) = 0 THEN PRINT " ISOL";
        IF GT(4, 1) = 1 THEN PRINT " SRC ";
        IF GT(4, 1) = 2 THEN PRINT " RCHG";
        LOCATE 18, 1
        PRINT "CO2 ";
        IF GT(5, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(5, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(5, 0);
        COLOR 11, 0:
        IF GT(5, 1) = 0 THEN PRINT " ISOL";
        IF GT(5, 1) = 1 THEN PRINT " SRC ";
        IF GT(5, 1) = 2 THEN PRINT " RCHG";
        LOCATE 19, 1
        PRINT "Ar  ";
        IF GT(6, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(6, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(6, 0);
        COLOR 11, 0:
        IF GT(6, 1) = 0 THEN PRINT " ISOL";
        IF GT(6, 1) = 1 THEN PRINT " SRC ";
        IF GT(6, 1) = 2 THEN PRINT " RCHG";
        LOCATE 20, 1
        PRINT "H2O ";
        IF GT(7, 0) < 30 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(7, 0) < 15 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(7, 0) - (water * 1.56);
        COLOR 11, 0:
        IF GT(7, 1) = 0 THEN PRINT " ISOL";
        IF GT(7, 1) = 1 THEN PRINT " SRC ";
        IF GT(7, 1) = 2 THEN PRINT " RCHG";
        LOCATE 21, 1
        PRINT "LPR ";
        IF GT(8, 0) > 50 THEN COLOR 14, 0 ELSE COLOR 10, 0
        IF GT(8, 0) > 80 THEN COLOR 12, 0
        PRINT USING "###.##"; GT(8, 0);
        COLOR 11, 0:
        IF GT(8, 1) = 0 THEN PRINT " ISOL";
        IF GT(8, 1) = 1 THEN PRINT " SRC ";
        IF GT(8, 1) = 2 THEN PRINT " VENT";
        LOCATE 22, 1: PRINT "probe:"; : COLOR 10, 0: PRINT probeNAME$(probe);
        LOCATE 23, 1: COLOR 11, 0: PRINT "pack: "; : COLOR 10, 0: PRINT packNAME$(pack - 1);

        t = 1
        FOR i = 1 TO 6
         FOR j = 1 TO 2
          LOCATE 20 + j, 13 + (i * 5) + INT(t / 11)
          IF tank(t) < 75 THEN fgclr = 14 ELSE fgclr = 10
          IF tank(t) < 50 THEN fgclr = 12
          IF tankRC(1) = t OR tankRC(2) = t THEN bkclr = 1 ELSE bkclr = 0
          COLOR fgclr, bkclr
          PRINT USING "###"; tank(t);
          COLOR 9, 0
          IF t < 10 THEN PRINT USING "#"; t; :    ELSE PRINT USING "##"; t;
         
          t = t + 1
         NEXT j
        NEXT i
        RETURN



500     'Sieverts per second
        del = 15
        runn = 29
        stp = 100
        vert = 20
        ofs = -30

        COLOR 2: LOCATE 1, 4: PRINT "Radiation Dose Rate versus Altitude for the Sun and Selected Planets";
        COLOR 7
        sx = 28: sy = 390: clr = 2: z$ = "Altitude in km": GOSUB 2100
        sx = 7: sy = 365: clr = 2: z$ = "Dose Rate in Sieverts per Second": GOSUB 2300
        sy = vert - (del * LOG(1)): sx = 20: clr = 2: z$ = "1": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -1)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-1": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -2)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-2": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -3)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-3": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -4)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-4": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -5)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-5": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -6)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-6": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -7)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-7": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -8)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-8": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -9)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-9": GOSUB 2300
        sy = vert - (del * LOG(10 ^ -10)) + 3: sx = 20: clr = 2: z$ = "10": GOSUB 2300
        sy = sy - 10: sx = 17: clr = 2: z$ = "-10": GOSUB 2300
      
      
        sx = (runn * LOG(1)) - ofs: sy = 380: clr = 2: z$ = "1": GOSUB 2100
        sx = (runn * LOG(10)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = (runn * LOG(100)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "2": GOSUB 2100
        sx = (runn * LOG(1000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "3": GOSUB 2100
        sx = (runn * LOG(10000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "4": GOSUB 2100
        sx = (runn * LOG(100000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "5": GOSUB 2100
        sx = (runn * LOG(1000000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "6": GOSUB 2100
        sx = (runn * LOG(10000000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "7": GOSUB 2100
        sx = (runn * LOG(100000000)) - ofs - 5: sy = 380: clr = 2: z$ = "10": GOSUB 2100
        sx = sx + 10: sy = 377: clr = 2: z$ = "8": GOSUB 2100


        FOR j = 0 TO 8
         strt = 10 ^ j
         stp = strt
         FOR i = strt TO strt * 10 STEP stp
          'IF i < 300 THEN 11
          LINE ((runn * LOG(i)) - ofs, vert - (del * LOG(10 ^ 0)))-((runn * LOG(i)) - ofs, vert - (del * LOG(10 ^ -10))), 1
         NEXT i
        NEXT j
        i = 1
       
        FOR j = -10 TO -1
        strt = 10 ^ j
        stp = strt
        FOR i = strt TO strt * 10 STEP stp
         LINE ((runn * LOG(1)) - ofs, vert - (del * LOG(i)))-((runn * LOG(1000000000)) - ofs, vert - (del * LOG(i))), 1
        NEXT i
        NEXT j
        i = 1
        LINE ((runn * LOG(1)) - ofs, vert - (del * LOG(i)))-((runn * LOG(1000000000)) - ofs, vert - (del * LOG(i))), 1
        i = 2.55E-09
       
        LINE ((runn * LOG(1)) - ofs, vert - (del * LOG(i)))-((runn * LOG(1000000000)) - ofs, vert - (del * LOG(i))), 15
       
        'Solar Proton Events (CMEs) up to 3.32e-7 @ mars; 9e-7 @ earth
        LINE (539, 21)-(630, 88), 0, BF
        LINE (539, 90)-(630, 157), 0, BF
       
        sx = 542: sy = 27: clr = 15: z$ = "Cosmic Background": GOSUB 2100
        sx = 547: sy = 37: clr = 14: z$ = "Sun": GOSUB 2100
        sx = 547: sy = 47: clr = 4: z$ = "Earth": GOSUB 2100
        sx = 547: sy = 57: clr = 6: z$ = "Jupiter": GOSUB 2100
        sx = 547: sy = 67: clr = 7: z$ = "Saturn": GOSUB 2100
        sx = 547: sy = 77: clr = 8: z$ = "Uranus": GOSUB 2100
        sx = 547: sy = 87: clr = 9: z$ = "Neptune": GOSUB 2100

        LINE (31, 63)-(395, 93), 0, BF
        sx = 34: sy = 70: clr = 2: z$ = "short-term exposure of 0.75 Sv will cause low level radiation sickness": GOSUB 2100
        sx = 34: sy = 80: clr = 2: z$ = "short-term exposure of 4 Sv will cause death": GOSUB 2100
        sx = 34: sy = 90: clr = 2: z$ = "long-term exposure of 1 Sv significantly increases long-term cancer risk": GOSUB 2100

        LINE (31, 125)-(249, 147), 0, BF
        sx = 34: sy = 133: clr = 2: z$ = "left and right arrow keys   select distance": GOSUB 2100
        sx = 34: sy = 143: clr = 2: z$ = "up and down arrow keys      select planet": GOSUB 2100


        LOCATE 27, 3: PRINT "DOSE RATE (Sv/s):  ";
        LOCATE 28, 3: PRINT "TIME to 1 Sv DOSE: ";
        LOCATE 25, 27: PRINT "OUTSIDE       INSIDE        SELECTED";
        COLOR 8
        LOCATE 26, 27: PRINT "w/ suit                     out w/ suit   inside";
        COLOR 7
     
        RESTORE 3000
        'earth
        READ z$
        READ x, y
        PSET (x, y), 4
        FOR i = 2 TO 256
          READ x, y
          LINE -(x, y), 4
        NEXT i

        'jupiter
        READ z$
        READ x, y
        PSET (x, y), 6
        FOR i = 2 TO 297
          READ x, y
          LINE -(x, y), 6
        NEXT i
      
        'Sun
        READ z$
        READ x, y
        PSET (x, y), 14
        FOR i = 2 TO 191
          READ x, y
          LINE -(x, y), 14
        NEXT i
        READ z$
        READ x, y
        PSET (x, y), 14
        FOR i = 2 TO 236
          READ x, y
          LINE -(x, y), 14
        NEXT i

        'saturn
        READ z$
        READ x, y
        PSET (x, y), 7
        FOR i = 2 TO 265
          READ x, y
          LINE -(x, y), 7
        NEXT i

        'uranus
        READ z$
        READ x, y
        PSET (x, y), 8
        FOR i = 2 TO 256
          READ x, y
          LINE -(x, y), 8
        NEXT i

        'neptune
        READ z$
        READ x, y
        PSET (x, y), 9
        FOR i = 2 TO 251
          READ x, y
          LINE -(x, y), 9
        NEXT i
        z$ = ""
        RETURN



400     LOCATE 25, 55
        sx = 542: sy = 97: clr = 2: z$ = "shielding": GOSUB 2100
        sx = 542: sy = 107: clr = 8 + (2 * SUIT): z$ = "S suit": GOSUB 2100
        sx = 542: sy = 117: clr = 8 + (2 * HAB): z$ = "H HAB": GOSUB 2100
        sx = 542: sy = 127: clr = 8 + (2 * MAG): z$ = "M MAGnetic": GOSUB 2100
        sx = 542: sy = 137: clr = 8 + (2 * AYSE): z$ = "A AYSE": GOSUB 2100
        sx = 542: sy = 147: clr = 8 + (2 * DISK): z$ = "D Disk": GOSUB 2100
        SHIELD = 1
        IF HAB = 1 THEN SHIELD = .1
        IF AYSE = 1 THEN SHIELD = .04
        IF SUIT = 1 THEN SHIELD = SHIELD * .5
        IF MAG = 1 THEN SHIELD = SHIELD / 5
        IF MAG = 1 AND AYSE = 1 THEN SHIELD = SHIELD / 3
        IF DISK = 1 THEN SHIELD = SHIELD / 5
       
        itr = 0
        IF OLDbug = bug THEN 401
        PSET (OLDbug, 368), 0
        LINE (OLDbug - 1, 369)-(OLDbug + 1, 369), 0
        LINE (OLDbug - 2, 370)-(OLDbug + 2, 370), 0
        PSET (28, Vbug), 0
        LINE (27, Vbug - 1)-(27, Vbug + 1), 0
        LINE (26, Vbug - 2)-(26, Vbug + 2), 0
        OLDbug = bug
        bugDIST = 2.718282 ^ ((bug + ofs) / runn)
        ON planet + 1 GOSUB 602, 603, 600, 601, 604, 605, 606
        COLOR 8
        LOCATE 25, 64: PRINT "("; : PRINT USING "##########"; bugDIST; : PRINT " km)";
        COLOR 7
        PSET (bug, 368), clr
        LINE (bug - 1, 369)-(bug + 1, 369), clr
        LINE (bug - 2, 370)-(bug + 2, 370), clr
        PSET (28, Vbug), clr
        LINE (27, Vbug - 1)-(27, Vbug + 1), clr
        LINE (26, Vbug - 2)-(26, Vbug + 2), clr


401     IF update = 0 THEN 411
        IF itr = 0 THEN z = RAD
        IF itr = 14 THEN z = RADin
        IF itr = 28 THEN z = cz
        IF itr = 42 THEN z = cz
        IF itr < 40 THEN LOCATE 27, 28 + itr: PRINT USING "##.###^^^^"; z;
        IF z = 0 THEN 411
        IF itr = 0 THEN z = 1 / (z * .5)
        IF itr = 14 THEN z = 1 / (z * 1)
        IF itr = 28 THEN z = 1 / (z * .5)
        IF itr = 42 THEN z = 1 / (z * SHIELD)
        LOCATE 28, 24 + itr
        IF z < 60 THEN PRINT USING "######.##"; z; : PRINT " s   "; : GOTO 410
        z = z / 60
        IF z < 60 THEN PRINT USING "######.##"; z; : PRINT " min "; : GOTO 410
        z = z / 60
        IF z < 24 THEN PRINT USING "######.##"; z; : PRINT " hr  "; : GOTO 410
        z = z / 24
        IF z < 365 THEN PRINT USING "######.##"; z; : PRINT " days"; : GOTO 410
        z = z / 365
        PRINT USING "######.##"; z; : PRINT " yrs ";
410     IF itr = 0 THEN itr = 14: GOTO 401
        IF itr = 14 THEN itr = 28: GOTO 401
        IF itr = 28 THEN itr = 42: GOTO 401
411     RETURN


2200    RESTORE 4000
        FOR j = 1 TO 44
         FOR i = 1 TO 16
          READ x, y
          letter(j, i, 1) = x
          letter(j, i, 2) = y
         NEXT i
        NEXT j
        RETURN

2300    z$ = UCASE$(z$)
        FOR i1 = 1 TO LEN(z$)
         y$ = MID$(z$, i1, 1)
         x = ASC(y$)
         IF x = 48 THEN x = 79
         IF x = 46 THEN x = 59
         IF x = 45 THEN x = 58
         IF x = 36 THEN x = 91
         IF x > 91 THEN x = 32
         j1 = x - 47
         IF j1 < 1 THEN 2301
         FOR k1 = 1 TO 16
          ly = letter(j1, k1, 1)
          lx = letter(j1, k1, 2)
          PSET (sx - lx, (sy - ly) - ((i1 - 1) * 5)), clr
         NEXT k1
2301    NEXT i1
        RETURN



2100    z$ = UCASE$(z$)
        FOR i1 = 1 TO LEN(z$)
         y$ = MID$(z$, i1, 1)
         x = ASC(y$)
         IF x = 48 THEN x = 79
         IF x = 46 THEN x = 59
         IF x = 45 THEN x = 58
         IF x = 36 THEN x = 91
         IF x > 91 THEN x = 32
         j1 = x - 47
         IF j1 < 1 THEN 2101
         FOR k1 = 1 TO 16
          lx = letter(j1, k1, 1)
          ly = letter(j1, k1, 2)
          PSET (((i1 - 1) * 5) + sx + lx, (sy - ly)), clr
         NEXT k1
2101    NEXT i1
        RETURN

4000    DATA 1,0, 0,1, 0,2, 0,3, 0,0, 0,4, 3,3, 3,2, 3,1, 1,0, 1,4, 2,4, 1,0, 2,0, 3,0, 3,4
        DATA 1,0, 2,0, 3,0, 2,1, 2,2, 2,3, 2,4, 1,4, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,4, 1,4, 2,4, 0,0, 0,0, 1,0, 2,0, 3,0, 1,1, 2,2, 0,0, 3,3, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 3,1, 3,1, 3,3, 0,0, 1,4, 2,4, 0,4, 0,0, 0,0, 0,0, 3,1, 1,2, 2,2, 1,0, 2,0
        DATA 0,2, 0,2, 0,2, 0,3, 0,4, 0,2, 0,2, 3,4, 3,3, 3,2, 3,1, 3,0, 1,2, 2,2, 0,2, 0,2
        DATA 0,0, 1,0, 2,0, 3,1, 2,2, 1,2, 0,3, 1,4, 2,4, 3,4, 0,4, 0,2, 0,0, 0,0, 0,0, 0,0
        DATA 0,1, 0,1, 0,2, 0,3, 0,4, 0,1, 0,1, 0,1, 0,1, 0,1, 3,1, 0,1, 1,2, 2,2, 1,0, 2,0
        DATA 0,4, 1,4, 2,4, 3,4, 3,3, 2,2, 1,1, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,1, 0,1, 0,1, 0,3, 0,1, 1,4, 2,4, 0,1, 3,3, 0,1, 3,1, 0,1, 1,2, 2,2, 1,0, 2,0
        DATA 3,3, 3,3, 3,2, 3,1, 3,0, 3,3, 3,3, 3,3, 3,3, 3,3, 0,3, 3,3, 2,2, 1,2, 2,4, 1,4
        DATA 1,2, 2,2, 3,2, 4,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2, 2,2
        DATA 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0, 2,0
        DATA 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 1,2, 2,2, 3,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2, 0,2
        DATA 0,0, 0,1, 0,2, 0,3, 0,0, 1,4, 2,4, 0,0, 3,3, 3,2, 3,1, 3,0, 1,2, 2,2, 0,0, 0,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 0,0, 3,3, 0,0, 3,1, 0,0, 1,2, 2,2, 1,0, 2,0
        DATA 0,1, 0,1, 0,2, 0,3, 0,1, 1,4, 2,4, 3,4, 0,1, 0,1, 0,1, 3,0, 0,1, 0,1, 1,0, 2,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 0,0, 3,3, 3,2, 3,1, 0,0, 0,0, 0,0, 1,0, 2,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 3,4, 0,0, 0,0, 0,0, 3,0, 1,2, 2,2, 1,0, 2,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 3,4, 0,0, 0,0, 0,0, 0,0, 1,2, 2,2, 0,0, 0,0
        DATA 0,1, 0,1, 0,2, 0,3, 0,1, 1,4, 2,4, 3,4, 0,1, 3,2, 3,1, 3,0, 0,1, 2,2, 1,0, 2,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 0,0, 0,0, 3,4, 3,3, 3,2, 3,1, 3,0, 1,2, 2,2, 0,0, 0,0
        DATA 1,0, 2,0, 3,0, 2,1, 2,2, 2,3, 2,4, 1,4, 3,4, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,0, 1,0, 2,0, 2,1, 2,2, 2,3, 2,4, 1,4, 3,4, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,2, 2,3, 3,4, 2,1, 3,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,0, 2,0, 3,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 3,4, 3,3, 3,2, 3,1, 3,0, 1,3, 2,3, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 3,4, 3,3, 3,2, 3,1, 3,0, 1,3, 2,2, 3,3, 0,0, 0,0, 0,0
        DATA 1,0, 0,1, 0,2, 0,3, 1,0, 1,0, 3,3, 3,2, 3,1, 1,0, 1,4, 2,4, 1,0, 2,0, 1,0, 1,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 3,3, 2,2, 1,2, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 1,0, 0,1, 0,2, 0,3, 1,0, 1,0, 3,3, 3,2, 3,1, 1,0, 1,4, 2,4, 1,0, 2,0, 3,0, 2,1
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 1,4, 2,4, 3,3, 2,2, 1,2, 2,1, 3,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 1,0, 2,0, 3,1, 2,2, 1,2, 0,3, 1,4, 2,4, 3,4, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,4, 1,4, 2,4, 1,3, 1,2, 1,1, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,4, 0,3, 0,2, 0,1, 1,0, 2,0, 3,1, 3,2, 3,3, 3,4, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,4, 0,3, 0,2, 1,1, 1,0, 2,0, 2,1, 3,2, 3,3, 3,4, 1,0, 1,0, 1,0, 1,0, 1,0, 1,0
        DATA 0,0, 0,1, 0,2, 0,3, 0,4, 3,4, 3,3, 3,2, 3,1, 3,0, 1,1, 2,1, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 1,1, 1,2, 2,3, 3,4, 0,4, 1,3, 1,2, 2,1, 3,0, 2,2, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,4, 1,3, 2,2, 1,1, 0,0, 3,3, 3,4, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0
        DATA 0,4, 1,4, 2,4, 3,4, 0,0, 1,0, 2,0, 3,0, 1,1, 1,2, 2,2, 2,3, 0,0, 0,0, 0,0, 0,0
        DATA 0,0, 1,0, 2,0, 3,1, 2,2, 1,2, 0,3, 1,4, 2,4, 3,4, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0


3000
DATA  earth
DATA   30 , 359 , 42 , 359 , 50 , 359 , 57 , 359 , 62 , 359 , 66 , 359 , 70 , 359 , 74 , 359 , 77 , 359 , 79 , 359 , 82 , 359
DATA   84 , 359 , 86 , 359 , 88 , 359 , 90 , 359 , 92 , 359 , 94 , 359 , 95 , 359 , 97 , 359 , 98 , 359 , 100 , 359 , 101 , 359
DATA   102 , 359 , 103 , 359 , 104 , 359 , 105 , 359 , 107 , 359 , 108 , 359 , 109 , 359 , 110 , 359 , 111 , 359 , 112 , 359 , 113 , 359
DATA   114 , 359 , 115 , 359 , 116 , 359 , 117 , 359 , 118 , 359 , 119 , 359 , 120 , 359 , 121 , 359 , 122 , 359 , 123 , 358 , 124 , 358
DATA   125 , 358 , 126 , 358 , 127 , 358 , 128 , 358 , 129 , 358 , 130 , 358 , 131 , 358 , 132 , 358 , 133 , 358 , 134 , 358 , 135 , 358
DATA   136 , 358 , 137 , 358 , 138 , 358 , 139 , 358 , 140 , 358 , 141 , 358 , 142 , 358 , 143 , 358 , 144 , 358 , 145 , 358 , 146 , 358
DATA   147 , 357 , 148 , 357 , 149 , 357 , 150 , 357 , 151 , 357 , 152 , 357 , 153 , 357 , 154 , 357 , 155 , 357 , 156 , 357 , 157 , 357
DATA   158 , 357 , 159 , 356 , 160 , 356 , 161 , 356 , 162 , 356 , 163 , 356 , 164 , 356 , 165 , 356 , 166 , 356 , 167 , 355 , 168 , 355
DATA   169 , 355 , 170 , 355 , 171 , 355 , 172 , 355 , 173 , 354 , 174 , 354 , 175 , 354 , 176 , 354 , 177 , 353 , 178 , 353 , 179 , 353
DATA   180 , 353 , 181 , 352 , 182 , 352 , 183 , 352 , 184 , 351 , 185 , 351 , 186 , 350 , 187 , 350 , 188 , 349 , 189 , 349 , 190 , 348
DATA   191 , 348 , 192 , 347 , 193 , 346 , 194 , 346 , 195 , 345 , 196 , 344 , 197 , 343 , 198 , 342 , 199 , 341 , 200 , 340 , 201 , 339
DATA   202 , 338 , 203 , 337 , 204 , 335 , 205 , 334 , 206 , 333 , 207 , 331 , 208 , 329 , 209 , 328 , 210 , 326 , 211 , 324 , 212 , 322
DATA   213 , 320 , 214 , 317 , 215 , 315 , 216 , 313 , 217 , 310 , 218 , 308 , 219 , 305 , 220 , 302 , 221 , 299 , 222 , 297 , 223 , 293
DATA   224 , 290 , 225 , 287 , 226 , 284 , 227 , 281 , 228 , 277 , 229 , 274 , 230 , 270 , 231 , 267 , 232 , 263 , 233 , 259 , 234 , 255
DATA   235 , 252 , 236 , 248 , 237 , 244 , 238 , 240 , 239 , 236 , 240 , 231 , 241 , 227 , 242 , 223 , 243 , 219 , 244 , 215 , 245 , 211
DATA   246 , 207 , 247 , 203 , 248 , 199 , 249 , 195 , 250 , 191 , 251 , 187 , 252 , 184 , 253 , 180 , 254 , 177 , 255 , 174 , 256 , 171
DATA   257 , 169 , 258 , 166 , 259 , 164 , 260 , 163 , 261 , 162 , 262 , 161 , 263 , 161 , 264 , 162 , 265 , 163 , 266 , 165 , 267 , 167
DATA   268 , 171 , 269 , 175 , 270 , 181 , 271 , 187 , 272 , 195 , 273 , 205 , 274 , 215 , 275 , 228 , 276 , 241 , 277 , 255 , 278 , 265
DATA   279 , 269 , 280 , 268 , 281 , 266 , 282 , 263 , 283 , 260 , 284 , 257 , 285 , 255 , 286 , 252 , 287 , 249 , 288 , 246 , 289 , 242
DATA   290 , 239 , 291 , 236 , 292 , 233 , 293 , 230 , 294 , 226 , 295 , 223 , 296 , 220 , 297 , 216 , 298 , 213 , 299 , 210 , 300 , 206
DATA   301 , 203 , 302 , 200 , 303 , 196 , 304 , 193 , 305 , 190 , 306 , 187 , 307 , 184 , 308 , 181 , 309 , 179 , 310 , 176 , 311 , 174
DATA   312 , 172 , 313 , 170 , 314 , 168 , 315 , 167 , 316 , 166 , 317 , 166 , 318 , 166 , 319 , 166 , 320 , 167 , 321 , 168 , 322 , 171
DATA   323 , 173 , 324 , 177 , 325 , 181 , 326 , 187 , 327 , 193 , 328 , 201 , 329 , 210 , 330 , 220 , 331 , 231 , 332 , 245 , 333 , 260
DATA   334 , 276 , 335 , 295 , 336 , 316
DATA  jupiter
DATA   30 , 248 , 82 , 248 , 100 , 248 , 110 , 248 , 118 , 248 , 124 , 248 , 130 , 248 , 134 , 248 , 138 , 248 , 141 , 248 , 144 , 248
DATA   147 , 248 , 149 , 248 , 152 , 248 , 154 , 248 , 156 , 248 , 157 , 248 , 159 , 248 , 161 , 248 , 162 , 248 , 164 , 248 , 165 , 248
DATA   167 , 248 , 168 , 248 , 169 , 248 , 170 , 248 , 171 , 248 , 172 , 248 , 174 , 248 , 175 , 248 , 176 , 248 , 177 , 248 , 178 , 248
DATA   179 , 248 , 180 , 248 , 181 , 248 , 182 , 248 , 183 , 248 , 184 , 248 , 185 , 248 , 186 , 248 , 187 , 248 , 188 , 248 , 189 , 248
DATA   190 , 248 , 191 , 248 , 192 , 248 , 193 , 248 , 194 , 248 , 195 , 248 , 196 , 248 , 197 , 248 , 198 , 248 , 199 , 248 , 200 , 248
DATA   201 , 248 , 202 , 248 , 203 , 248 , 204 , 248 , 205 , 248 , 206 , 248 , 207 , 248 , 208 , 248 , 209 , 248 , 210 , 248 , 211 , 248
DATA   212 , 248 , 213 , 248 , 214 , 248 , 215 , 248 , 216 , 248 , 217 , 248 , 218 , 248 , 219 , 248 , 220 , 248 , 221 , 248 , 222 , 248
DATA   223 , 248 , 224 , 248 , 225 , 248 , 226 , 248 , 227 , 248 , 228 , 248 , 229 , 248 , 230 , 248 , 231 , 248 , 232 , 248 , 233 , 248
DATA   234 , 248 , 235 , 248 , 236 , 248 , 237 , 248 , 238 , 248 , 239 , 248 , 240 , 247 , 241 , 247 , 242 , 247 , 243 , 247 , 244 , 247
DATA   245 , 247 , 246 , 247 , 247 , 247 , 248 , 247 , 249 , 247 , 250 , 247 , 251 , 247 , 252 , 247 , 253 , 247 , 254 , 247 , 255 , 247
DATA   256 , 247 , 257 , 247 , 258 , 247 , 259 , 247 , 260 , 247 , 261 , 247 , 262 , 247 , 263 , 247 , 264 , 247 , 265 , 247 , 266 , 246
DATA   267 , 246 , 268 , 246 , 269 , 246 , 270 , 246 , 271 , 246 , 272 , 246 , 273 , 246 , 274 , 246 , 275 , 246 , 276 , 246 , 277 , 246
DATA   278 , 246 , 279 , 245 , 280 , 245 , 281 , 245 , 282 , 245 , 283 , 245 , 284 , 245 , 285 , 245 , 286 , 245 , 287 , 245 , 288 , 244
DATA   289 , 244 , 290 , 244 , 291 , 244 , 292 , 244 , 293 , 244 , 294 , 244 , 295 , 243 , 296 , 243 , 297 , 243 , 298 , 243 , 299 , 243
DATA   300 , 242 , 301 , 242 , 302 , 242 , 303 , 242 , 304 , 242 , 305 , 241 , 306 , 241 , 307 , 241 , 308 , 241 , 309 , 240 , 310 , 240
DATA   311 , 240 , 312 , 240 , 313 , 239 , 314 , 239 , 315 , 239 , 316 , 238 , 317 , 238 , 318 , 238 , 319 , 237 , 320 , 237 , 321 , 236
DATA   322 , 236 , 323 , 236 , 324 , 235 , 325 , 235 , 326 , 234 , 327 , 234 , 328 , 233 , 329 , 233 , 330 , 232 , 331 , 232 , 332 , 231
DATA   333 , 230 , 334 , 230 , 335 , 229 , 336 , 228 , 337 , 228 , 338 , 227 , 339 , 226 , 340 , 225 , 341 , 225 , 342 , 224 , 343 , 223
DATA   344 , 222 , 345 , 221 , 346 , 220 , 347 , 219 , 348 , 218 , 349 , 217 , 350 , 216 , 351 , 215 , 352 , 214 , 353 , 213 , 354 , 212
DATA   355 , 210 , 356 , 209 , 357 , 208 , 358 , 206 , 359 , 205 , 360 , 203 , 361 , 202 , 362 , 200 , 363 , 199 , 364 , 197 , 365 , 195
DATA   366 , 194 , 367 , 192 , 368 , 190 , 369 , 188 , 370 , 186 , 371 , 184 , 372 , 182 , 373 , 180 , 374 , 178 , 375 , 176 , 376 , 174
DATA   377 , 172 , 378 , 170 , 379 , 167 , 380 , 165 , 381 , 163 , 382 , 160 , 383 , 158 , 384 , 156 , 385 , 153 , 386 , 151 , 387 , 148
DATA   388 , 146 , 389 , 144 , 390 , 141 , 391 , 139 , 392 , 136 , 393 , 134 , 394 , 132 , 395 , 130 , 396 , 128 , 397 , 126 , 398 , 124
DATA   399 , 122 , 400 , 120 , 401 , 119 , 402 , 118 , 403 , 116 , 404 , 116 , 405 , 115 , 406 , 115 , 407 , 114 , 408 , 115 , 409 , 115
DATA   410 , 116 , 411 , 117 , 412 , 118 , 413 , 120 , 414 , 122 , 415 , 123 , 416 , 125 , 417 , 126 , 418 , 127 , 419 , 128 , 420 , 129
DATA   421 , 130 , 422 , 131 , 423 , 132 , 424 , 133 , 425 , 135 , 426 , 138 , 427 , 141 , 428 , 145 , 429 , 149 , 430 , 154 , 431 , 160
DATA   432 , 167 , 433 , 174 , 434 , 183 , 435 , 193 , 436 , 204 , 437 , 217 , 438 , 231 , 439 , 246 , 440 , 264 , 441 , 283 , 442 , 316
DATA  sun1
DATA   390 , 20 , 392 , 22 , 393 , 24 , 394 , 26 , 395 , 28 , 396 , 29 , 397 , 31 , 398 , 33 , 399 , 36 , 400 , 37 , 401 , 39
DATA   402 , 40 , 403 , 42 , 404 , 44 , 405 , 46 , 406 , 48 , 407 , 49 , 408 , 52 , 409 , 53 , 410 , 55 , 411 , 56 , 412 , 58
DATA   413 , 60 , 414 , 62 , 415 , 64 , 416 , 66 , 417 , 67 , 418 , 69 , 419 , 71 , 420 , 73 , 421 , 75 , 422 , 76 , 423 , 78
DATA   424 , 80 , 425 , 81 , 426 , 83 , 427 , 85 , 428 , 87 , 429 , 89 , 430 , 91 , 431 , 92 , 432 , 94 , 433 , 96 , 434 , 98
DATA   435 , 100 , 436 , 102 , 437 , 103 , 438 , 105 , 439 , 107 , 440 , 109 , 441 , 110 , 442 , 112 , 443 , 114 , 444 , 116 , 445 , 118
DATA   446 , 119 , 447 , 121 , 448 , 123 , 449 , 125 , 450 , 126 , 451 , 128 , 452 , 130 , 453 , 132 , 454 , 134 , 455 , 135 , 456 , 137
DATA   457 , 139 , 458 , 141 , 459 , 143 , 460 , 144 , 461 , 146 , 462 , 148 , 463 , 150 , 464 , 151 , 465 , 153 , 466 , 155 , 467 , 157
DATA   468 , 158 , 469 , 160 , 470 , 162 , 471 , 164 , 472 , 166 , 473 , 167 , 474 , 169 , 475 , 171 , 476 , 172 , 477 , 174 , 478 , 176
DATA   479 , 178 , 480 , 179 , 481 , 181 , 482 , 183 , 483 , 185 , 484 , 186 , 485 , 188 , 486 , 190 , 487 , 191 , 488 , 193 , 489 , 195
DATA   490 , 196 , 491 , 198 , 492 , 200 , 493 , 201 , 494 , 203 , 495 , 205 , 496 , 206 , 497 , 208 , 498 , 210 , 499 , 211 , 500 , 213
DATA   501 , 214 , 502 , 216 , 503 , 218 , 504 , 219 , 505 , 221 , 506 , 222 , 507 , 224 , 508 , 225 , 509 , 227 , 510 , 229 , 511 , 230
DATA   512 , 232 , 513 , 233 , 514 , 235 , 515 , 236 , 516 , 238 , 517 , 239 , 518 , 240 , 519 , 242 , 520 , 243 , 521 , 245 , 522 , 246
DATA   523 , 248 , 524 , 249 , 525 , 250 , 526 , 252 , 527 , 253 , 528 , 254 , 529 , 256 , 530 , 257 , 531 , 258 , 532 , 260 , 533 , 261
DATA   534 , 262 , 535 , 264 , 536 , 265 , 537 , 266 , 538 , 267 , 539 , 269 , 540 , 270 , 541 , 271 , 542 , 272 , 543 , 274 , 544 , 275
DATA   545 , 276 , 546 , 277 , 547 , 279 , 548 , 280 , 549 , 281 , 550 , 282 , 551 , 283 , 552 , 284 , 553 , 286 , 554 , 287 , 555 , 288
DATA   556 , 289 , 557 , 290 , 558 , 291 , 559 , 292 , 560 , 294 , 561 , 295 , 562 , 296 , 563 , 297 , 564 , 298 , 565 , 299 , 566 , 300
DATA   567 , 301 , 568 , 302 , 569 , 303 , 570 , 305 , 571 , 306 , 572 , 307 , 573 , 308 , 574 , 309 , 575 , 310 , 576 , 311 , 577 , 312
DATA   578 , 313 , 579 , 314 , 580 , 315 , 581 , 316
DATA  sun2
DATA   396 , 30 , 397 , 31 , 398 , 32 , 399 , 33 , 400 , 34 , 401 , 35 , 402 , 35 , 403 , 36 , 404 , 37 , 405 , 38 , 406 , 39
DATA   407 , 40 , 408 , 41 , 409 , 42 , 410 , 43 , 411 , 43 , 412 , 44 , 413 , 45 , 414 , 46 , 415 , 47 , 416 , 48 , 417 , 49
DATA   418 , 50 , 419 , 51 , 420 , 52 , 421 , 52 , 422 , 53 , 423 , 54 , 424 , 55 , 425 , 56 , 426 , 57 , 427 , 58 , 428 , 59
DATA   429 , 60 , 430 , 61 , 431 , 61 , 432 , 62 , 433 , 63 , 434 , 64 , 435 , 65 , 436 , 66 , 437 , 67 , 438 , 68 , 439 , 69
DATA   440 , 69 , 441 , 70 , 442 , 71 , 443 , 72 , 444 , 73 , 445 , 74 , 446 , 75 , 447 , 76 , 448 , 77 , 449 , 78 , 450 , 79
DATA   451 , 79 , 452 , 80 , 453 , 81 , 454 , 82 , 455 , 83 , 456 , 84 , 457 , 85 , 458 , 86 , 459 , 87 , 460 , 88 , 461 , 88
DATA   462 , 89 , 463 , 90 , 464 , 91 , 465 , 92 , 466 , 93 , 467 , 94 , 468 , 95 , 469 , 96 , 470 , 97 , 471 , 98 , 472 , 98
DATA   473 , 99 , 474 , 100 , 475 , 101 , 476 , 102 , 477 , 103 , 478 , 104 , 479 , 105 , 480 , 106 , 481 , 107 , 482 , 107 , 483 , 108
DATA   484 , 109 , 485 , 110 , 486 , 111 , 487 , 112 , 488 , 113 , 489 , 114 , 490 , 115 , 491 , 116 , 492 , 117 , 493 , 117 , 494 , 118
DATA   495 , 119 , 496 , 120 , 497 , 121 , 498 , 122 , 499 , 123 , 500 , 124 , 501 , 125 , 502 , 126 , 503 , 126 , 504 , 127 , 505 , 128
DATA   506 , 129 , 507 , 130 , 508 , 131 , 509 , 132 , 510 , 133 , 511 , 134 , 512 , 135 , 513 , 136 , 514 , 136 , 515 , 137 , 516 , 138
DATA   517 , 139 , 518 , 140 , 519 , 141 , 520 , 142 , 521 , 143 , 522 , 144 , 523 , 145 , 524 , 145 , 525 , 146 , 526 , 147 , 527 , 148
DATA   528 , 149 , 529 , 150 , 530 , 151 , 531 , 152 , 532 , 153 , 533 , 154 , 534 , 155 , 535 , 155 , 536 , 156 , 537 , 157 , 538 , 158
DATA   539 , 159 , 540 , 160 , 541 , 161 , 542 , 162 , 543 , 163 , 544 , 164 , 545 , 164 , 546 , 165 , 547 , 166 , 548 , 167 , 549 , 168
DATA   550 , 169 , 551 , 170 , 552 , 171 , 553 , 172 , 554 , 173 , 555 , 174 , 556 , 174 , 557 , 175 , 558 , 176 , 559 , 177 , 560 , 178
DATA   561 , 179 , 562 , 180 , 563 , 181 , 564 , 182 , 565 , 183 , 566 , 183 , 567 , 184 , 568 , 185 , 569 , 186 , 570 , 187 , 571 , 188
DATA   572 , 189 , 573 , 190 , 574 , 191 , 575 , 192 , 576 , 193 , 577 , 193 , 578 , 194 , 579 , 195 , 580 , 196 , 581 , 197 , 582 , 198
DATA   583 , 199 , 584 , 200 , 585 , 201 , 586 , 202 , 587 , 202 , 588 , 203 , 589 , 204 , 590 , 205 , 591 , 206 , 592 , 207 , 593 , 208
DATA   594 , 209 , 595 , 210 , 596 , 211 , 597 , 212 , 598 , 212 , 599 , 213 , 600 , 214 , 601 , 215 , 602 , 216 , 603 , 217 , 604 , 218
DATA   605 , 219 , 606 , 220 , 607 , 221 , 608 , 222 , 609 , 222 , 610 , 223 , 611 , 224 , 612 , 225 , 613 , 226 , 614 , 227 , 615 , 228
DATA   616 , 229 , 617 , 230 , 618 , 231 , 619 , 231 , 620 , 232 , 621 , 233 , 622 , 234 , 623 , 235 , 624 , 236 , 625 , 237 , 626 , 238
DATA   627 , 239 , 628 , 240 , 629 , 241 , 630 , 241 , 631 , 242
DATA  saturn
DATA   30 , 321 , 82 , 321 , 100 , 321 , 110 , 321 , 118 , 321 , 124 , 321 , 130 , 321 , 134 , 321 , 138 , 321 , 141 , 321 , 144 , 321
DATA   147 , 321 , 149 , 321 , 152 , 321 , 154 , 321 , 156 , 321 , 157 , 321 , 159 , 321 , 161 , 321 , 162 , 321 , 164 , 321 , 165 , 321
DATA   167 , 321 , 168 , 321 , 169 , 321 , 170 , 321 , 171 , 321 , 172 , 321 , 174 , 321 , 175 , 321 , 176 , 321 , 177 , 321 , 178 , 321
DATA   179 , 321 , 180 , 321 , 181 , 321 , 182 , 321 , 183 , 321 , 184 , 321 , 185 , 321 , 186 , 321 , 187 , 321 , 188 , 321 , 189 , 320
DATA   190 , 320 , 191 , 320 , 192 , 320 , 193 , 320 , 194 , 320 , 195 , 320 , 196 , 320 , 197 , 320 , 198 , 320 , 199 , 320 , 200 , 320
DATA   201 , 320 , 202 , 320 , 203 , 320 , 204 , 320 , 205 , 320 , 206 , 320 , 207 , 320 , 208 , 320 , 209 , 320 , 210 , 320 , 211 , 320
DATA   212 , 320 , 213 , 320 , 214 , 320 , 215 , 320 , 216 , 320 , 217 , 320 , 218 , 320 , 219 , 320 , 220 , 320 , 221 , 320 , 222 , 320
DATA   223 , 320 , 224 , 320 , 225 , 320 , 226 , 320 , 227 , 320 , 228 , 320 , 229 , 319 , 230 , 319 , 231 , 319 , 232 , 319 , 233 , 319
DATA   234 , 319 , 235 , 319 , 236 , 319 , 237 , 319 , 238 , 319 , 239 , 319 , 240 , 319 , 241 , 319 , 242 , 319 , 243 , 319 , 244 , 319
DATA   245 , 319 , 246 , 318 , 247 , 318 , 248 , 318 , 249 , 318 , 250 , 318 , 251 , 318 , 252 , 318 , 253 , 318 , 254 , 318 , 255 , 318
DATA   256 , 317 , 257 , 317 , 258 , 317 , 259 , 317 , 260 , 317 , 261 , 317 , 262 , 317 , 263 , 317 , 264 , 316 , 265 , 316 , 266 , 316
DATA   267 , 316 , 268 , 316 , 269 , 316 , 270 , 315 , 271 , 315 , 272 , 315 , 273 , 315 , 274 , 315 , 275 , 314 , 276 , 314 , 277 , 314
DATA   278 , 314 , 279 , 313 , 280 , 313 , 281 , 313 , 282 , 313 , 283 , 312 , 284 , 312 , 285 , 312 , 286 , 311 , 287 , 311 , 288 , 311
DATA   289 , 310 , 290 , 310 , 291 , 310 , 292 , 309 , 293 , 309 , 294 , 308 , 295 , 308 , 296 , 307 , 297 , 307 , 298 , 307 , 299 , 306
DATA   300 , 306 , 301 , 305 , 302 , 304 , 303 , 304 , 304 , 303 , 305 , 303 , 306 , 302 , 307 , 301 , 308 , 301 , 309 , 300 , 310 , 299
DATA   311 , 299 , 312 , 298 , 313 , 297 , 314 , 296 , 315 , 296 , 316 , 295 , 317 , 294 , 318 , 293 , 319 , 292 , 320 , 291 , 321 , 290
DATA   322 , 289 , 323 , 288 , 324 , 287 , 325 , 286 , 326 , 285 , 327 , 283 , 328 , 282 , 329 , 281 , 330 , 280 , 331 , 278 , 332 , 277
DATA   333 , 275 , 334 , 274 , 335 , 272 , 336 , 271 , 337 , 269 , 338 , 268 , 339 , 266 , 340 , 264 , 341 , 262 , 342 , 260 , 343 , 259
DATA   344 , 257 , 345 , 255 , 346 , 253 , 347 , 250 , 348 , 248 , 349 , 246 , 350 , 244 , 351 , 242 , 352 , 239 , 353 , 237 , 354 , 234
DATA   355 , 232 , 356 , 229 , 357 , 227 , 358 , 224 , 359 , 221 , 360 , 218 , 361 , 215 , 362 , 213 , 363 , 210 , 364 , 207 , 365 , 204
DATA   366 , 201 , 367 , 198 , 368 , 195 , 369 , 192 , 370 , 188 , 371 , 185 , 372 , 182 , 373 , 179 , 374 , 176 , 375 , 173 , 376 , 170
DATA   377 , 167 , 378 , 164 , 379 , 161 , 380 , 158 , 381 , 156 , 382 , 153 , 383 , 151 , 384 , 149 , 385 , 147 , 386 , 145 , 387 , 143
DATA   388 , 142 , 389 , 141 , 390 , 141 , 391 , 140 , 392 , 140 , 393 , 141 , 394 , 142 , 395 , 144 , 396 , 147 , 397 , 150 , 398 , 153
DATA   399 , 158 , 400 , 164 , 401 , 170 , 402 , 178 , 403 , 187 , 404 , 197 , 405 , 209 , 406 , 222 , 407 , 237 , 408 , 254 , 409 , 273
DATA   410 , 316
DATA  uranus
DATA   30 , 327 , 82 , 327 , 100 , 327 , 110 , 327 , 118 , 327 , 124 , 327 , 130 , 327 , 134 , 327 , 138 , 327 , 141 , 327 , 144 , 327
DATA   147 , 327 , 149 , 327 , 152 , 327 , 154 , 327 , 156 , 327 , 157 , 327 , 159 , 327 , 161 , 327 , 162 , 327 , 164 , 327 , 165 , 327
DATA   167 , 327 , 168 , 327 , 169 , 327 , 170 , 327 , 171 , 327 , 172 , 327 , 174 , 327 , 175 , 327 , 176 , 327 , 177 , 327 , 178 , 327
DATA   179 , 327 , 180 , 327 , 181 , 327 , 182 , 327 , 183 , 327 , 184 , 327 , 185 , 327 , 186 , 327 , 187 , 327 , 188 , 327 , 189 , 327
DATA   190 , 327 , 191 , 327 , 192 , 327 , 193 , 327 , 194 , 327 , 195 , 326 , 196 , 326 , 197 , 326 , 198 , 326 , 199 , 326 , 200 , 326
DATA   201 , 326 , 202 , 326 , 203 , 326 , 204 , 326 , 205 , 326 , 206 , 326 , 207 , 326 , 208 , 326 , 209 , 326 , 210 , 326 , 211 , 326
DATA   212 , 326 , 213 , 326 , 214 , 326 , 215 , 326 , 216 , 326 , 217 , 326 , 218 , 326 , 219 , 326 , 220 , 326 , 221 , 326 , 222 , 326
DATA   223 , 326 , 224 , 326 , 225 , 325 , 226 , 325 , 227 , 325 , 228 , 325 , 229 , 325 , 230 , 325 , 231 , 325 , 232 , 325 , 233 , 325
DATA   234 , 325 , 235 , 325 , 236 , 325 , 237 , 325 , 238 , 325 , 239 , 324 , 240 , 324 , 241 , 324 , 242 , 324 , 243 , 324 , 244 , 324
DATA   245 , 324 , 246 , 324 , 247 , 324 , 248 , 324 , 249 , 323 , 250 , 323 , 251 , 323 , 252 , 323 , 253 , 323 , 254 , 323 , 255 , 323
DATA   256 , 322 , 257 , 322 , 258 , 322 , 259 , 322 , 260 , 322 , 261 , 322 , 262 , 321 , 263 , 321 , 264 , 321 , 265 , 321 , 266 , 321
DATA   267 , 320 , 268 , 320 , 269 , 320 , 270 , 320 , 271 , 319 , 272 , 319 , 273 , 319 , 274 , 319 , 275 , 318 , 276 , 318 , 277 , 318
DATA   278 , 317 , 279 , 317 , 280 , 317 , 281 , 316 , 282 , 316 , 283 , 315 , 284 , 315 , 285 , 315 , 286 , 314 , 287 , 314 , 288 , 313
DATA   289 , 313 , 290 , 312 , 291 , 312 , 292 , 311 , 293 , 311 , 294 , 310 , 295 , 310 , 296 , 309 , 297 , 309 , 298 , 308 , 299 , 307
DATA   300 , 307 , 301 , 306 , 302 , 305 , 303 , 304 , 304 , 304 , 305 , 303 , 306 , 302 , 307 , 301 , 308 , 300 , 309 , 299 , 310 , 299
DATA   311 , 298 , 312 , 297 , 313 , 296 , 314 , 295 , 315 , 293 , 316 , 292 , 317 , 291 , 318 , 290 , 319 , 289 , 320 , 288 , 321 , 286
DATA   322 , 285 , 323 , 283 , 324 , 282 , 325 , 281 , 326 , 279 , 327 , 278 , 328 , 276 , 329 , 274 , 330 , 273 , 331 , 271 , 332 , 269
DATA   333 , 267 , 334 , 265 , 335 , 264 , 336 , 262 , 337 , 260 , 338 , 258 , 339 , 255 , 340 , 253 , 341 , 251 , 342 , 249 , 343 , 246
DATA   344 , 244 , 345 , 242 , 346 , 239 , 347 , 237 , 348 , 234 , 349 , 231 , 350 , 229 , 351 , 226 , 352 , 223 , 353 , 220 , 354 , 217
DATA   355 , 215 , 356 , 212 , 357 , 209 , 358 , 206 , 359 , 203 , 360 , 200 , 361 , 197 , 362 , 194 , 363 , 191 , 364 , 188 , 365 , 185
DATA   366 , 182 , 367 , 179 , 368 , 176 , 369 , 173 , 370 , 170 , 371 , 168 , 372 , 165 , 373 , 163 , 374 , 161 , 375 , 158 , 376 , 157
DATA   377 , 155 , 378 , 154 , 379 , 153 , 380 , 152 , 381 , 151 , 382 , 151 , 383 , 152 , 384 , 153 , 385 , 154 , 386 , 156 , 387 , 159
DATA   388 , 162 , 389 , 166 , 390 , 171 , 391 , 177 , 392 , 184 , 393 , 192 , 394 , 201 , 395 , 212 , 396 , 224 , 397 , 238 , 398 , 253
DATA   399 , 270 , 400 , 290 , 401 , 316
DATA  neptune
DATA   30 , 312 , 82 , 312 , 100 , 312 , 110 , 312 , 118 , 312 , 124 , 312 , 130 , 312 , 134 , 312 , 138 , 312 , 141 , 312 , 144 , 312
DATA   147 , 312 , 149 , 312 , 152 , 312 , 154 , 311 , 156 , 311 , 157 , 311 , 159 , 311 , 161 , 311 , 162 , 311 , 164 , 311 , 165 , 311
DATA   167 , 311 , 168 , 311 , 169 , 311 , 170 , 311 , 171 , 311 , 172 , 311 , 174 , 311 , 175 , 311 , 176 , 311 , 177 , 311 , 178 , 311
DATA   179 , 311 , 180 , 311 , 181 , 311 , 182 , 311 , 183 , 311 , 184 , 311 , 185 , 311 , 186 , 311 , 187 , 311 , 188 , 311 , 189 , 311
DATA   190 , 311 , 191 , 311 , 192 , 311 , 193 , 311 , 194 , 311 , 195 , 311 , 196 , 311 , 197 , 311 , 198 , 311 , 199 , 311 , 200 , 311
DATA   201 , 311 , 202 , 311 , 203 , 311 , 204 , 311 , 205 , 311 , 206 , 311 , 207 , 311 , 208 , 311 , 209 , 311 , 210 , 311 , 211 , 311
DATA   212 , 311 , 213 , 311 , 214 , 311 , 215 , 310 , 216 , 310 , 217 , 310 , 218 , 310 , 219 , 310 , 220 , 310 , 221 , 310 , 222 , 310
DATA   223 , 310 , 224 , 310 , 225 , 310 , 226 , 310 , 227 , 310 , 228 , 310 , 229 , 310 , 230 , 310 , 231 , 310 , 232 , 310 , 233 , 309
DATA   234 , 309 , 235 , 309 , 236 , 309 , 237 , 309 , 238 , 309 , 239 , 309 , 240 , 309 , 241 , 309 , 242 , 309 , 243 , 309 , 244 , 308
DATA   245 , 308 , 246 , 308 , 247 , 308 , 248 , 308 , 249 , 308 , 250 , 308 , 251 , 308 , 252 , 307 , 253 , 307 , 254 , 307 , 255 , 307
DATA   256 , 307 , 257 , 307 , 258 , 307 , 259 , 306 , 260 , 306 , 261 , 306 , 262 , 306 , 263 , 306 , 264 , 305 , 265 , 305 , 266 , 305
DATA   267 , 305 , 268 , 304 , 269 , 304 , 270 , 304 , 271 , 304 , 272 , 303 , 273 , 303 , 274 , 303 , 275 , 302 , 276 , 302 , 277 , 302
DATA   278 , 302 , 279 , 301 , 280 , 301 , 281 , 300 , 282 , 300 , 283 , 300 , 284 , 299 , 285 , 299 , 286 , 298 , 287 , 298 , 288 , 297
DATA   289 , 297 , 290 , 296 , 291 , 296 , 292 , 295 , 293 , 295 , 294 , 294 , 295 , 294 , 296 , 293 , 297 , 292 , 298 , 292 , 299 , 291
DATA   300 , 290 , 301 , 290 , 302 , 289 , 303 , 288 , 304 , 287 , 305 , 287 , 306 , 286 , 307 , 285 , 308 , 284 , 309 , 283 , 310 , 282
DATA   311 , 281 , 312 , 280 , 313 , 279 , 314 , 278 , 315 , 277 , 316 , 276 , 317 , 275 , 318 , 273 , 319 , 272 , 320 , 271 , 321 , 270
DATA   322 , 268 , 323 , 267 , 324 , 265 , 325 , 264 , 326 , 262 , 327 , 261 , 328 , 259 , 329 , 258 , 330 , 256 , 331 , 254 , 332 , 253
DATA   333 , 251 , 334 , 249 , 335 , 247 , 336 , 245 , 337 , 243 , 338 , 241 , 339 , 239 , 340 , 237 , 341 , 235 , 342 , 232 , 343 , 230
DATA   344 , 228 , 345 , 225 , 346 , 223 , 347 , 221 , 348 , 218 , 349 , 216 , 350 , 213 , 351 , 211 , 352 , 208 , 353 , 205 , 354 , 203
DATA   355 , 200 , 356 , 198 , 357 , 195 , 358 , 192 , 359 , 190 , 360 , 187 , 361 , 185 , 362 , 182 , 363 , 180 , 364 , 177 , 365 , 175
DATA   366 , 173 , 367 , 170 , 368 , 168 , 369 , 166 , 370 , 165 , 371 , 163 , 372 , 162 , 373 , 161 , 374 , 160 , 375 , 159 , 376 , 159
DATA   377 , 159 , 378 , 159 , 379 , 160 , 380 , 162 , 381 , 163 , 382 , 166 , 383 , 169 , 384 , 173 , 385 , 177 , 386 , 183 , 387 , 189
DATA   388 , 196 , 389 , 205 , 390 , 214 , 391 , 225 , 392 , 237 , 393 , 251 , 394 , 267 , 395 , 284 , 396 , 316
DATA   end


        'earth
600     m1 = 3000
        s1 = 540
        m2 = 20000
        s2 = 3990
        a3 = .111  '350000
        b3 = .61  '350000
        x = -1
        az = (bugDIST - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3   '3500000
        b = (bugDIST - m2) ^ 2
        b = b / (2 * s2 * s2)
        b = 2.81 ^ (-1 * b)
        b = b / (2.5 * s2)
        b = b * b3   '35000000
        sx = 541: sy = 47: clr = 4: z$ = "-": GOSUB 2100
        sx = 541: sy = 57: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 37: clr = 0: z$ = "-": GOSUB 2100
        sx = 562: sy = 37: clr = 0: z$ = " flare": GOSUB 2100
        IF bug > 335 THEN cz = 2.55E-09: clr = 15 ELSE cz = az + b: clr = 4
        Vbug = vert - (del * LOG(cz))
        RETURN
       
        'jupiter
601     m1 = 421000
        s1 = 98000
        m2 = 671000
        s2 = 165100
        a3 = 400 '1110   '35000000000#
        b3 = 270 '1110   '35000000000#
        az = (bugDIST - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        b = (bugDIST - m2) ^ 2
        b = b / (2 * s2 * s2)
        b = 2.81 ^ (-1 * b)
        b = b / (2.5 * s2)
        b = b * b3
        sx = 541: sy = 67: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 47: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 57: clr = 6: z$ = "-": GOSUB 2100
        IF bug > 442 THEN cz = 2.55E-09: clr = 15 ELSE cz = az + b: clr = 6
        Vbug = vert - (del * LOG(cz))
        RETURN

        'Sun
602     m1 = 0
        s1 = 880000
        a3 = 350000000000#
        az = 7.9E+18 / (bugDIST ^ 3.5)
        cz = az + ((7.7E+07 / bugDIST) / bugDIST)
        sx = 541: sy = 37: clr = 14: z$ = "-": GOSUB 2100
        sx = 562: sy = 37: clr = 0: z$ = " flare": GOSUB 2100
        sx = 541: sy = 87: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 47: clr = 0: z$ = "-": GOSUB 2100
        IF bug > 581 THEN cz = 2.55E-09: clr = 15 ELSE clr = 14
        Vbug = vert - (del * LOG(cz))
        IF Vbug < 20 THEN Vbug = 20
        RETURN

603     IF bug < 398 THEN 602
        cz = 1.998E+09 / (bugDIST ^ 1.75)
        Vbug = vert - (del * LOG(cz))
        sx = 541: sy = 37: clr = 14: z$ = "-": GOSUB 2100
        sx = 562: sy = 37: clr = 14: z$ = " flare": GOSUB 2100
        sx = 541: sy = 47: clr = 0: z$ = "-": GOSUB 2100
        clr = 14
        IF Vbug < 20 THEN Vbug = 20
        RETURN

        'saturn
604     m1 = 251000
        s1 = 52000
        a3 = 42.75     '1570000000#
        az = (bugDIST - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        cz = az
        sx = 541: sy = 57: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 67: clr = 7: z$ = "-": GOSUB 2100
        sx = 541: sy = 77: clr = 0: z$ = "-": GOSUB 2100
        IF bug > 410 THEN cz = 2.55E-09: clr = 15 ELSE clr = 7
        Vbug = vert - (del * LOG(cz))

        RETURN

        'uranus
605     m1 = 181000
        s1 = 38000
        a3 = 15.06    '570000000#
        az = (bugDIST - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        cz = az
        sx = 541: sy = 67: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 77: clr = 8: z$ = "-": GOSUB 2100
        sx = 541: sy = 87: clr = 0: z$ = "-": GOSUB 2100
        IF bug > 400 THEN cz = 2.55E-09: clr = 15 ELSE clr = 8
        Vbug = vert - (del * LOG(cz))
        RETURN

        'neptune
606     m1 = 151000
        s1 = 34000
        a3 = 8.14     '320000000#
        az = (bugDIST - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        cz = az
        sx = 541: sy = 37: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 77: clr = 0: z$ = "-": GOSUB 2100
        sx = 541: sy = 87: clr = 9: z$ = "-": GOSUB 2100
        IF bug > 396 THEN cz = 2.55E-09: clr = 15 ELSE clr = 9
        Vbug = vert - (del * LOG(cz))
        RETURN


2000    'IF ERL = 97 THEN RESUME 98
        'IF ERL = 190 THEN RESUME 191
        'IF ERL = 191 THEN RESUME 192
        'IF ERL = 180 THEN CLOSE #1: RESUME 180
        CLS
        PRINT "line="; ERL
        PRINT "error="; ERR
        z$ = INPUT$(1)
        END




6100    OPEN "I", #1, "eecomINI"
        FOR i = 1 TO 585
         INPUT #1, z$
        NEXT i
        FOR i = 1 TO 84
         INPUT #1, x, y, z
         LOCATE y, x: PRINT CHR$(z);
        NEXT i
        CLOSE #1
        RETURN


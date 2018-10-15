711     ON ERROR GOTO 2000
        DEFDBL X-Y
        DIM a(5), c(7), ch(7, 29), d(9), dr(10, 5), Fire(8), n(6, 10), dw(10), de(10), da(10, 16), loc$(39), thickness(39), RAD(39), refDEN(39), refALT(39)
        DIM ASTROrad(8), ASTROstat(8), zAs(8), starN(10), ASTROhealth%(8, 7), temp(6)
        DIM x(39) AS DOUBLE
        DIM y(39) AS DOUBLE
        dim inpSTR AS STRING
        FOR i = 1 TO 10: starN(i) = -1: NEXT i
        locate 1,1,0
712     OPEN "I", #1, "starsr"
        FOR i = 1 TO 3021
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
        NEXT i
        FOR i = 1 TO 241
         INPUT #1, z
         INPUT #1, z
        NEXT i
        FOR i = 0 TO 39
         INPUT #1, z
         IF z = 14 THEN starnum = starnum + 1: starN(starnum) = i
         INPUT #1, z
         INPUT #1, RAD(i)
         INPUT #1, refDEN(i)
         INPUT #1, refALT(i)
         INPUT #1, thickness(i)
        NEXT i
        INPUT #1, year, day, hour, min, sec
        FOR i = 0 TO 35
         INPUT #1, z1, z2, z3, z4, z5, z6
        NEXT i
        FOR i = 0 TO 39
         INPUT #1, loc$(i)
        NEXT i
        CLOSE #1
      
        star = 3
        a(0) = 10
        a(1) = 14
        a(2) = 12
        a(3) = 2
        a(4) = 2
        FOR i = 1 TO 8
         da(i, 3) = 205
         da(i, 4) = 254
         da(i, 14) = 249
         da(i, 13) = 32
         ASTROhealth%(i, 7) = 3
        NEXT i
        da(2, 3) = 186
        da(7, 3) = 186
        da(8, 3) = 186
        c(1) = 0: ch(1, 9) = 6 * 1.5 * 2.2 * 1000
        c(2) = 0: ch(2, 9) = 3.5 * 3 * 2.2 * 1000
        c(3) = 0: ch(3, 9) = 1.6 * 4.3 * 2.2 * 1000
        c(4) = 0: ch(4, 9) = 1.5 * 1.8 * 2.2 * 1000
        c(5) = 0: ch(5, 9) = 1.1 * 2.3 * 2.2 * 1000
        c(6) = 0: ch(6, 9) = 1.1 * 2.1 * 2.2 * 1000
        d(1) = 0
        d(2) = 0
        d(3) = 0
        d(4) = 0
        d(5) = 0
        d(6) = 0
        d(7) = 0
        d(8) = 0
        d(9) = 0
        dr(1, 4) = 1: dr(1, 5) = 0
        dr(2, 4) = 2: dr(2, 5) = 1
        dr(3, 4) = 2: dr(3, 5) = 3
        dr(4, 4) = 2: dr(4, 5) = 4
        dr(5, 4) = 2: dr(5, 5) = 5
        dr(6, 4) = 5: dr(6, 5) = 0
        dr(7, 4) = 2: dr(7, 5) = 6
        dr(8, 4) = 2: dr(8, 5) = 2
        cmp = 1
        var = 1
        ch(0, 9) = 100000000
        oldtime# = -1
        flare = 1
        DELtemp = 7
        astro = 1
        astroHval = 1
        flarewarn = 0
        flareOCTANT = 1
        inpSTR = space$(1000)
        outSTR$ = space$(1000)
        chkCHAR1$ = " "
        chkCHAR2$ = " "
        OLDlocation = -100
       
        ' Load input data files
        CLS
        OPEN "I", #1, "EECOM.DAT"
        IF EOF(1) THEN pathname$ = "" ELSE INPUT #1, pathname$  'Location of Habitat EECOM program
        IF EOF(1) THEN Zpath$ = "" ELSE INPUT #1, Zpath$        'Location of Habitat ORBIT program
        CLOSE #1

        'Look for alternate input filenames for server controlled system reset
        OPEN "R", #1, Zpath$ + "OSBACKUP.RND", 8
        aOS$=space$(8)
        GET #1, 1, aOS$
        reset$ = right$(aOS$,7)
        aOS$ = left$(aOS$,1)+"ORBIT5S"
        PUT #1, 1, aOS$
        CLOSE #1

                  
        IF reset$ = "XXXXXYY" THEN filename$ = "gasRS1.RND" ELSE filename$ = "GASSIM.RND"
716     open "R", #1, filename$, 182
        inpSTR=space$(182)
        GET #1, 1, inpSTR
        close #1
        if len(inpSTR) <> 182 then cls:print "Compartment error code file ";filename$;" is corrupt.":zz$=input$(1):end
        
        chkCHAR1$=left$(inpSTR,1)
        chkCHAR2$=right$(inpSTR,1)
        if chkCHAR1$<>chkCHAR2$ then cls:print "Compartment error code file ";filename$;" check bytes do not match.":zz$=input$(1):end

        k=2
        FOR i = 1 TO 6
         ch(i, 18) = cvs(mid$(inpSTR,k,4)):k=k+4            'holes in compartment
         ch(i, 19) = cvs(mid$(inpSTR,k,4)):k=k+4            'oxygen variances
         ch(i, 20) = cvs(mid$(inpSTR,k,4)):k=k+4            'carbon dioxide variance
         ch(i, 21) = cvs(mid$(inpSTR,k,4)):k=k+4            'water variance
         ch(i, 22) = cvs(mid$(inpSTR,k,4)):k=k+4            'chemical hazards variance
         ch(i, 23) = cvs(mid$(inpSTR,k,4)):k=k+4            'dust variance
         ch(i, 24) = cvs(mid$(inpSTR,k,4)):k=k+4            'biohazard variance
         Fire(i) = cvi(mid$(inpSTR,k,4)):k=k+2
        NEXT i

       
        IF reset$ = "XXXXXYY" THEN filename$ = "gasRS2.RND" ELSE filename$ = "doorsim.RND"
717     OPEN "R", #1, filename$, 276
        inpSTR=space$(276)
        GET #1, 1, inpSTR
        close #1
        if len(inpSTR) <> 276 then cls:print "Misc. error code file ";filename$;" is corrupt.":zz$=input$(1):end
        
        chkCHAR1$=left$(inpSTR,1)
        chkCHAR2$=right$(inpSTR,1)
        if chkCHAR1$<>chkCHAR2$ then cls:print "Misc. error code file ";filename$;" check bytes do not match.":zz$=input$(1):end

        k=18
        lightning = cvi(mid$(inpSTR,k,2)):k=k+2
        Asteroid = cvi(mid$(inpSTR,k,2)):k=k+2
        WIND = cvi(mid$(inpSTR,k,2)):k=k+2
        dustX = cvi(mid$(inpSTR,k,2)):k=k+2
        DELtemp = cvi(mid$(inpSTR,k,2)):k=k+2
        discharge = cvi(mid$(inpSTR,k,2)):k=k+2
        water = cvi(mid$(inpSTR,k,2)):k=k+2
        
        flarewarn = cvi(mid$(inpSTR,k,2)):k=k+2
        flareOCTANT = cvi(mid$(inpSTR,k,2)):k=k+2
        flareSIZE = cvi(mid$(inpSTR,k,2)):k=k+2
        warn = cvi(mid$(inpSTR,k,2)):k=k+2
        delATM = cvi(mid$(inpSTR,k,2)):k=k+2

        atm = cvs(mid$(inpSTR,k,4)):k=k+4
        RADout= cvs(mid$(inpSTR,k,4)):k=k+4
        RADin= cvs(mid$(inpSTR,k,4)):k=k+4
        FOR i = 1 TO 8
         ASTROrad(i)= cvs(mid$(inpSTR,k,4)):k=k+4
        NEXT i
        FOR i = 1 TO 8
         FOR j = 1 TO 7
          ASTROhealth%(i, j) = cvi(mid$(inpSTR,k,2)):k=k+2
         NEXT j
        NEXT i
        k=k+58
        star = cvi(mid$(inpSTR,k,2)):k=k+2
        flare = cvl(mid$(inpSTR,k,4)):k=k+4
        cosmicFACTOR = cvl(mid$(inpSTR,k,4)):k=k+4
        location = cvi(mid$(inpSTR,k,2)):k=k+2


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
         ch(i, 0) = 101.325
         ch(i, 1) = .7852
         ch(i, 2) = .1926
         ch(i, 3) = .0003
         ch(i, 4) = .0096
         ch(i, 5) = .0123
         ch(i, 6) = 0
         ch(i, 7) = .15
         ch(i, 8) = 0
         ch(i, 10) = ch(i, 0) * ch(i, 9) / (298 * 8.31)
         FOR j = 1 TO 5
          n(i, j) = ch(i, j) * ch(i, 10)
         NEXT j
         n(i, 6) = ch(i, 6) * ch(i, 9)
         n(i, 7) = ch(i, 7) * ch(i, 9)
         n(i, 8) = ch(i, 8) * ch(i, 9)
        NEXT i
        ch(1, 12) = 2: ch(1, 13) = -1
        ch(2, 12) = 7: ch(2, 13) = 2
        ch(3, 12) = 7: ch(3, 13) = 7
        ch(4, 12) = 7: ch(4, 13) = -1
        ch(5, 12) = 12: ch(5, 13) = -1
        ch(6, 12) = 14: ch(6, 13) = 2
        dr(1, 1) = 1: dr(1, 2) = 0
        dr(2, 1) = 2: dr(2, 2) = 1
        dr(3, 1) = 2: dr(3, 2) = 3
        dr(4, 1) = 2: dr(4, 2) = 4
        dr(5, 1) = 2: dr(5, 2) = 5
        dr(6, 1) = 5: dr(6, 2) = 0
        dr(7, 1) = 2: dr(7, 2) = 6
        dr(8, 1) = 2: dr(8, 2) = 2
        door = 1

        clr = 8
        IF Asteroid = 1 THEN clr = 14
        IF Asteroid = 2 THEN clr = 12
        COLOR clr, 0: LOCATE 1, 72: PRINT "ASTEROID";
        IF ABS(ch(dr(door, 1), 0) - ch(dr(door, 2), 0)) > 10 THEN COLOR 12, 0:   ELSE COLOR 8, 0
        LOCATE 14, 10: PRINT door; "PRESS";
        COLOR 7, 0
        COLOR 8 + (DOORoverride * 4), 0
        LOCATE 15, 11: PRINT "OVERRIDE";
        IF de(door) = 10 THEN COLOR 12, 0 ELSE COLOR 8, 0
        LOCATE 13, 10: PRINT door; "MALF ";
        COLOR 8, 0
        LOCATE 17, 11: PRINT loc$(location);
        COLOR 7, 0
        ttl = TIMER - 6
        GOSUB 200
       
1       ttt = TIMER

80      OPEN "I", #1, "eecomwrn.txt"
        IF NOT EOF(1) THEN INPUT #1, eecomwarning1$
        IF NOT EOF(1) THEN INPUT #1, eecomwarning2$
        CLOSE #1
        IF LEN(eecomwarning1$) > 25 THEN eecomwarning1$ = LEFT$(eecomwarning1$, 25)
        IF LEN(eecomwarning2$) > 25 THEN eecomwarning2$ = LEFT$(eecomwarning2$, 25)
        IF LEN(eecomwarning1$) < 25 THEN eecomwarning1$ = eecomwarning1$ + SPACE$(25 - LEN(eecomwarning1$))
        IF LEN(eecomwarning2$) < 25 THEN eecomwarning2$ = eecomwarning2$ + SPACE$(25 - LEN(eecomwarning2$))


        'Input EECOM telemetry data
        '---------------------------------------------
81      k=0
        open "R", #1, "gastelemetry.rnd",800
        inpSTR=space$(800)
        k=k+1
        get #1, 1, inpSTR
        close #1
        chkCHAR1$=left$(inpSTR,1)
        chkCHAR2$=right$(inpSTR,1)
        if chkCHAR1$=chkCHAR2$ then 82
        if k<5 then 81
        locate 25,1
        color 14,0
        print "Telem File Error ";
        goto 120
        
        
82      k=2
        FOR i = 0 TO 6
         FOR j = 1 TO 8
           n(i,j)=CVS(mid$(inpSTR,k,4))
           k=k+4
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         dw(i)=CVi(mid$(inpSTR,k,2))
         if dw(i)=13 then dw(i)=3
         if dw(i)=14 then dw(i)=4
         k=k+2
        NEXT i
        k=k+18
        OAT = CVS(mid$(inpSTR,k,4)):k=k+40
        temp(0)=OAT
        FOR i = 1 TO 6
         ch(i,29) = CVS(mid$(inpSTR,k,4)):k=k+4
        NEXT i
        k=k+52
        FOR i = 1 TO 6
         FIREtmp = CVi(mid$(inpSTR,k,2)):k=k+2
         temp(i) = CVi(mid$(inpSTR,k,2)):k=k+2
         LOCATE i + 4, 17
         IF FIREtmp > 0.1 THEN COLOR 12, 0 ELSE COLOR 7, 0
         PRINT USING "###"; temp(i) - 273;
        NEXT i
        '---------------------------------------------

        FOR i = 0 TO 6
         ch(i, 0) = 0
         FOR j = 1 TO 6
          ch(i, j) = (n(i, j) * 8.31 * temp(i) / ch(i, 9))
          ch(i, 0) = ch(i, 0) + ch(i, j)
         NEXT j
         FOR j = 1 TO 6
          IF ch(i, 0) > 0 THEN ch(i, j) = ch(i, j) / ch(i, 0)
         NEXT j
         'ch(i, 6) = n(i, 6) / ch(i, 9)
         ch(i, 7) = n(i, 7) / ch(i, 9)
         ch(i, 8) = n(i, 8) / ch(i, 9)
        NEXT i

        'warnings
        '--------
120     FOR i = 1 TO 6
         c(i) = 0
         IF ch(i, 0) < 97 THEN c(i) = 1
         IF ch(i, 0) > 110 THEN c(i) = 1
         IF ch(i, 3) * ch(i, 0) < .005 THEN c(i) = 1
         IF ch(i, 3) * ch(i, 0) > .5 THEN c(i) = 1
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
       
        COLOR 7, 0
        GOSUB 200
        GOSUB 660
        IF discharge = 1 THEN discharge = 0: GOSUB 660
       

111     z$ = INKEY$
        IF z$ = "" THEN 112
        IF z$ = "," THEN z$ = "<"
        IF z$ = "." THEN z$ = ">"
        IF z$ = CHR$(27) THEN END
        IF z$ = CHR$(0) + CHR$(134) THEN GOSUB 6000: GOSUB 660
        IF z$ = CHR$(0) + "P" THEN cmp = cmp + 1: IF cmp = 7 THEN cmp = 1
        IF z$ = CHR$(0) + "H" THEN cmp = cmp - 1: IF cmp = 0 THEN cmp = 6
        IF z$ = CHR$(0) + "M" THEN var = var + 1: IF var = 8 THEN var = 1
        IF z$ = CHR$(0) + "K" THEN var = var - 1: IF var = 0 THEN var = 7
        IF z$ = CHR$(0) + "G" THEN door = door + 1: IF door = 9 THEN door = 1
        IF z$ = CHR$(0) + "O" THEN door = door - 1: IF door = 0 THEN door = 8
        IF z$ = "*" THEN DOORoverride = 1 - DOORoverride
        IF UCASE$(z$) = "F" THEN Fire(cmp) = Fire(cmp) + 1000: update = 1
        IF Fire(cmp) > 5000 THEN Fire(cmp) = 0
        IF z$ = CHR$(13) THEN GOSUB 500
        IF z$ = CHR$(0) + "R" THEN GOSUB 600
        IF z$ = CHR$(0) + "S" THEN GOSUB 610
        if ucase$(z$) = "M" then gosub 650
        if z$ = "r" then Rst = 1: update = 1
        if z$ = "R" then Rst = 2: update = 1
        IF z$ = CHR$(0) + "B" THEN Asteroid = 0: GOSUB 660
        IF z$ = CHR$(0) + "C" THEN Asteroid = 1: GOSUB 660
        IF z$ = CHR$(0) + "D" THEN Asteroid = 2: GOSUB 660
        IF UCASE$(z$) = "+" THEN del = 1: GOSUB 300
        IF UCASE$(z$) = "-" THEN del = 1: GOSUB 400
        IF z$ = CHR$(0) + "I" THEN del = 100: GOSUB 300
        IF z$ = CHR$(0) + "Q" THEN del = 100: GOSUB 400
        IF z$ = "<" AND flare > 1 THEN flare = flare / 2
        IF z$ = ">" AND flare < 10000000 THEN flare = flare * 2
        IF z$ = CHR$(0) + "<" THEN astro = astro - 1: IF astro = 0 THEN astro = 8
        IF z$ = CHR$(0) + "=" THEN astro = astro + 1: IF astro = 9 THEN astro = 1
        IF z$ = CHR$(0) + ">" THEN astroHval = astroHval - 1: IF astroHval = 0 THEN astroHval = 6
        IF z$ = CHR$(0) + "?" THEN astroHval = astroHval + 1: IF astroHval = 7 THEN astroHval = 1
        IF z$ = CHR$(0) + "@" AND ASTROhealth%(astro, astroHval) > -3 THEN ASTROhealth%(astro, astroHval) = ASTROhealth%(astro, astroHval) - 1
        IF z$ = CHR$(0) + "A" AND ASTROhealth%(astro, astroHval) < 3 THEN ASTROhealth%(astro, astroHval) = ASTROhealth%(astro, astroHval) + 1
        IF z$ = "}" AND dustX < 7 THEN dustX = dustX + 1: GOSUB 660
        IF z$ = "{" AND dustX > 0 THEN dustX = dustX - 1: GOSUB 660
        IF z$ = "(" AND delATM > -63 THEN delATM = delATM - 1: GOSUB 660
        IF z$ = ")" AND delATM < 63 THEN delATM = delATM + 1: GOSUB 660
        IF z$ = "w" AND lightning < 5 THEN lightning = lightning + 1: GOSUB 660
        IF z$ = "q" AND lightning > 0 THEN lightning = lightning - 1: GOSUB 660
        IF z$ = "s" AND DELtemp < 15 THEN DELtemp = DELtemp + 1: GOSUB 660
        IF z$ = "a" AND DELtemp > 0 THEN DELtemp = DELtemp - 1: GOSUB 660
        IF z$ = "d" THEN discharge = 1: GOSUB 660
        IF cosmicFACTOR > 100 THEN Cfact = 10 ELSE Cfact = 1
        IF cosmicFACTOR > 1000 THEN Cfact = 100
        IF cosmicFACTOR > 10000 THEN Cfact = 1000
        IF cosmicFACTOR > 100000 THEN Cfact = 10000
        IF cosmicFACTOR > 1000000 THEN Cfact = 100000
        IF z$ = "c" AND cosmicFACTOR > 0 THEN cosmicFACTOR = cosmicFACTOR - Cfact
        IF z$ = "C" AND cosmicFACTOR < 10000000 THEN cosmicFACTOR = cosmicFACTOR + Cfact
        IF z$ = "[" THEN star = star - 1: IF star = 0 THEN star = starnum
        IF z$ = "]" THEN star = star + 1: IF star > starnum THEN star = 1
        IF z$ = CHR$(0) + ";" THEN warn = 1 - warn
        IF z$ = "/" THEN flareSIZE = flareSIZE + 1: IF flareSIZE > 5 THEN flareSIZE = 0
        IF z$ = "=" THEN flareOCTANT = flareOCTANT + 1: IF flareOCTANT = 9 THEN flareOCTANT = 1
        IF z$ = "1" THEN ASTROhealth%(1, 7) = cmp
        IF z$ = "2" THEN ASTROhealth%(2, 7) = cmp
        IF z$ = "3" THEN ASTROhealth%(3, 7) = cmp
        IF z$ = "4" THEN ASTROhealth%(4, 7) = cmp
        IF z$ = "5" THEN ASTROhealth%(5, 7) = cmp
        IF z$ = "6" THEN ASTROhealth%(6, 7) = cmp
        IF z$ = "7" THEN ASTROhealth%(7, 7) = cmp
        IF z$ = "8" THEN ASTROhealth%(8, 7) = cmp
        IF z$ = "z" AND water > 0 THEN water = water - 1
        IF z$ = "x" THEN water = water + 1
        COLOR 7, 0
        GOSUB 200
  
112     IF TIMER - ttl > 5 THEN GOSUB 8000: ttl = TIMER
        IF TIMER - ttt > 1 THEN 1
        GOTO 111

        'Add to environmental variances
        '------------------------------
300     IF var = 1 THEN ch(cmp, 18) = ch(cmp, 18) + (.001 * del)   'holes in compartment
        IF ABS(ch(cmp, 18)) < .001 THEN ch(cmp, 18) = 0
        IF var = 2 THEN ch(cmp, 19) = ch(cmp, 19) + (.001 * del)  'oxygen variances
        IF ABS(ch(cmp, 19)) < .001 THEN ch(cmp, 19) = 0
        IF var = 3 THEN ch(cmp, 20) = ch(cmp, 20) + (.001 * del)  'carbon dioxide variance
        IF ABS(ch(cmp, 20)) < .001 THEN ch(cmp, 20) = 0
        IF var = 4 THEN ch(cmp, 21) = ch(cmp, 21) + (.001 * del)  'water variance
        IF ABS(ch(cmp, 21)) < .001 THEN ch(cmp, 21) = 0
        IF var = 5 THEN ch(cmp, 22) = ch(cmp, 22) + (.1 * del)    'dust variance
        IF ABS(ch(cmp, 22)) < .1 THEN ch(cmp, 22) = 0
        IF ch(cmp, 22) > 900 THEN ch(cmp, 22) = 900
        IF var = 6 THEN ch(cmp, 23) = ch(cmp, 23) + (.1 * del)    'chemical hazards variance
        IF ABS(ch(cmp, 23)) < .1 THEN ch(cmp, 23) = 0
        IF var = 7 THEN ch(cmp, 24) = ch(cmp, 24) + (.1 * del)    'biohazard variance
        IF ABS(ch(cmp, 24)) < .1 THEN ch(cmp, 24) = 0
        update = 1
        RETURN
        '------------------------------

        'Take from environmenal variences
        '--------------------------------
400     IF var = 1 THEN ch(cmp, 18) = ch(cmp, 18) - (.001 * del)   'holes in compartment
        IF ABS(ch(cmp, 18)) < .001 THEN ch(cmp, 18) = 0
        IF var = 2 THEN ch(cmp, 19) = ch(cmp, 19) - (.001 * del)  'oxygen variances
        IF ABS(ch(cmp, 19)) < .001 THEN ch(cmp, 19) = 0
        IF var = 3 THEN ch(cmp, 20) = ch(cmp, 20) - (.001 * del)  'carbon dioxide variance
        IF ABS(ch(cmp, 20)) < .001 THEN ch(cmp, 20) = 0
        IF var = 4 THEN ch(cmp, 21) = ch(cmp, 21) - (.001 * del)  'water variance
        IF ABS(ch(cmp, 21)) < .001 THEN ch(cmp, 21) = 0
        IF var = 5 THEN ch(cmp, 22) = ch(cmp, 22) - (.1 * del)   'dust variance
        IF ABS(ch(cmp, 22)) < .1 THEN ch(cmp, 22) = 0
        IF var = 6 THEN ch(cmp, 23) = ch(cmp, 23) - (.1 * del)   'chemical hazards variance
        IF ABS(ch(cmp, 23)) < .1 THEN ch(cmp, 23) = 0
        IF var = 7 THEN ch(cmp, 24) = ch(cmp, 24) - (.1 * del)   'biohazard variance
        IF ABS(ch(cmp, 24)) < .1 THEN ch(cmp, 24) = 0

        update = 1
        RETURN
        '--------------------------------
       
        'print error codes
        '-----------------
500     update = 0
        chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        if Rst = 1 then Rst = 0:chkBYTE=0: update = 1
        if Rst = 2 then Rst = 0:chkBYTE=59: update = 1
        outSTR$=chr$(chkBYTE+64)
        FOR i = 1 TO 6
         outSTR$=outSTR$+mks$(ch(i, 18))            'holes in compartment
         outSTR$=outSTR$+mks$(ch(i, 19))            'oxygen variances
         outSTR$=outSTR$+mks$(ch(i, 20))            'carbon dioxide variance
         outSTR$=outSTR$+mks$(ch(i, 21))            'water variance
         outSTR$=outSTR$+mks$(ch(i, 22))            'chemical hazards variance
         outSTR$=outSTR$+mks$(ch(i, 23))            'dust variance
         outSTR$=outSTR$+mks$(ch(i, 24))            'biohazard variance
         outSTR$=outSTR$+mki$(Fire(i))
        NEXT i
        outSTR$=outSTR$+chr$(chkBYTE+64)
        OPEN "R", #1, pathname$ + "GASSIM.RND",182
        put #1, 1, outSTR$
        CLOSE #1
        RETURN
        '-----------------
       
        'print door error codes
        '----------------------
600     IF ABS(ch(dr(door, 1), 0) - ch(dr(door, 2), 0)) > 10 AND DOORoverride = 0 THEN 601
        IF d(door) = 4 THEN d(door) = 0 ELSE d(door) = 4
        GOSUB 660
601     RETURN

610     if d(door) = 3 then d(door) = 0 else d(door) = 3
        gosub 660
        return

650     IF de(door) = 0 THEN de(door) = 10 ELSE de(door) = 0

660     chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$=chr$(chkBYTE+64)
        
        FOR i = 1 TO 8
         dd = d(i)+de(i)
         'IF d(i) = 4 THEN dd = dd + 1
         'IF de(i) = 10 THEN dd = dd + 2
         outSTR$=outSTR$+mki$(dd)
        NEXT i
        outSTR$=outSTR$+mki$(lightning)
        outSTR$=outSTR$+mki$(Asteroid)
        outSTR$=outSTR$+mki$(WIND)
        outSTR$=outSTR$+mki$(dustX)
        outSTR$=outSTR$+mki$(DELtemp)
        outSTR$=outSTR$+mki$(discharge)
        outSTR$=outSTR$+mki$(water)
        
        outSTR$=outSTR$+mki$(flarewarn)
        outSTR$=outSTR$+mki$(flareOCTANT)
        outSTR$=outSTR$+mki$(flareSIZE)
        outSTR$=outSTR$+mki$(warn)
        outSTR$=outSTR$+mki$(delATM)

        outSTR$=outSTR$+mks$(atm)
        outSTR$=outSTR$+mks$(RADout)
        outSTR$=outSTR$+mks$(RADin)
        FOR i = 1 TO 8
         outSTR$=outSTR$+mks$(ASTROrad(i))
        NEXT i
        FOR i = 1 TO 8
         FOR j = 1 TO 7
          outSTR$=outSTR$+mki$(ASTROhealth%(i, j))
         NEXT j
        NEXT i
        outSTR$=outSTR$+loc$(starN(star))
        outSTR$=outSTR$+eecomwarning1$
        outSTR$=outSTR$+eecomwarning2$

        outSTR$=outSTR$+mki$(star)
        outSTR$=outSTR$+mkl$(flare)
        outSTR$=outSTR$+mkl$(cosmicFACTOR)
        outSTR$=outSTR$+mki$(location)
        outSTR$=outSTR$+mki$(0)
        outSTR$=outSTR$+mki$(0)
        outSTR$=outSTR$+mks$(0)
        outSTR$=outSTR$+chr$(chkBYTE+64)
        OPEN "R", #1, pathname$ + "DOORSIM.RND",276
        put #1, 1, outSTR$
        CLOSE #1
        RETURN


          

200     LOCATE 1, 1
        PRINT CHR$(218); STRING$(4, 196); CHR$(194); STRING$(4, 196); CHR$(194);
        IF de(6) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 6 THEN drbk = drbk + 1
        IF ABS(ch(dr(6, 1), 0) - ch(dr(6, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(6) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT STRING$(2, da(6, dw(6))); : COLOR 7, 0
      
        PRINT STRING$(2, 196); CHR$(191)
        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 4 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(4)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 5 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(5)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179)
      
        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 4 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(4)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 5 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(5)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179)

        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(195);
        IF de(4) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 4 THEN drbk = drbk + 1
        IF ABS(ch(dr(4, 1), 0) - ch(dr(4, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(4) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT STRING$(2, da(4, dw(4))); : COLOR 7, 0
        PRINT CHR$(196); : PRINT CHR$(196); : PRINT CHR$(193);
        IF de(5) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 5 THEN drbk = drbk + 1
        IF ABS(ch(dr(5, 1), 0) - ch(dr(5, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(5) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT STRING$(2, da(5, dw(5))); : COLOR 7, 0
        PRINT CHR$(194); : PRINT CHR$(196); : PRINT CHR$(180)

        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 2 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(2)), 0: PRINT STRING$(7, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 6 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(6)), 0: PRINT STRING$(1, chrt); : COLOR 7, 0
        PRINT CHR$(179)


        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        IF de(2) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 2 THEN drbk = drbk + 1
        IF ABS(ch(dr(2, 1), 0) - ch(dr(2, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(2) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT CHR$(da(2, dw(2))); : COLOR 7, 0
        IF cmp = 2 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(2)), 0: PRINT STRING$(7, chrt); : COLOR 7, 0
        IF de(7) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 7 THEN drbk = drbk + 1
        IF ABS(ch(dr(7, 1), 0) - ch(dr(7, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(7) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT CHR$(da(7, dw(7))); : COLOR 7, 0
        IF cmp = 6 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(6)), 0: PRINT STRING$(1, chrt); : COLOR 7, 0
        PRINT CHR$(179)


        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        IF de(2) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 2 THEN drbk = drbk + 1
        IF ABS(ch(dr(2, 1), 0) - ch(dr(2, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(2) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT CHR$(da(2, dw(2))); : COLOR 7, 0
        IF cmp = 2 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(2)), 0: PRINT STRING$(7, chrt); : COLOR 7, 0
        PRINT CHR$(195); CHR$(196);
        PRINT CHR$(180)

        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 2 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(2)), 0: PRINT STRING$(7, chrt); : COLOR 7, 0
        IF de(8) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 8 THEN drbk = drbk + 1
        IF ABS(ch(dr(8, 1), 0) - ch(dr(8, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(8) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT CHR$(da(8, dw(8))); : COLOR 7, 0
        IF cmp = 2 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(2)), 0: PRINT STRING$(1, chrt); : COLOR 7, 0
        PRINT CHR$(179)

        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(195); STRING$(5, 196);
        IF de(3) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 3 THEN drbk = drbk + 1
        IF ABS(ch(dr(3, 1), 0) - ch(dr(3, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(3) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT STRING$(2, da(3, dw(3))); : COLOR 7, 0
        PRINT CHR$(193); CHR$(196); CHR$(180)


        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 3 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(3)), 0: PRINT STRING$(9, chrt); : COLOR 7, 0
        PRINT CHR$(179)

        PRINT CHR$(179);
        IF cmp = 1 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(1)), 0: PRINT STRING$(4, chrt); : COLOR 7, 0
        PRINT CHR$(179);
        IF cmp = 3 THEN chrt = 219 ELSE chrt = 177
        COLOR a(c(3)), 0: PRINT STRING$(9, chrt); : COLOR 7, 0
        PRINT CHR$(179)


        PRINT CHR$(192); : PRINT CHR$(196); : PRINT CHR$(196);
        IF de(1) = 10 THEN drbk = 4 ELSE drbk = 0
        IF door = 1 THEN drbk = drbk + 1
        IF ABS(ch(dr(1, 1), 0) - ch(dr(1, 2), 0)) > 10 THEN drfg = 12 ELSE drfg = 2
        IF dw(1) AND 4 THEN drfg = 0
        COLOR drfg, drbk: PRINT STRING$(2, da(1, dw(1))); : COLOR 7, 0
        PRINT CHR$(193); STRING$(9, 196); CHR$(217)
       
        COLOR 9, 0
        LOCATE 3, 20: PRINT "    Press     N2      O2     CO2     Ar   H2O  chem dust  bio";
        COLOR 7, 0
       
        FOR i = 0 TO 6
         IF cmp = i THEN clbk = 1 ELSE clbk = 0
         COLOR 7, clbk
         IF i = 0 THEN 210
         LOCATE 3 + ch(i, 13), ch(i, 12)
         IF ch(i, 29) < -1 THEN PRINT "V";
         IF ch(i, 29) > -2 AND ch(i, 29) < 0 THEN PRINT "v";
         IF ch(i, 29) > 0 AND ch(i, 29) < 2 THEN PRINT "p";
         IF ch(i, 29) = 2 THEN PRINT "P";
210      LOCATE 4 + i, 20:
         IF i > 0 THEN PRINT USING "##_ "; i;  ELSE PRINT "AM ";
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


        'COLOR 9, 0
        'LOCATE 12, 25
        'PRINT "LEAK             O2     CO2          H2O  CHEM DUST  BIO";
        COLOR 7, 0
        FOR i = 1 TO 6
         LOCATE 10 + i, 21
         IF var = 1 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 18) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "###.###"; ch(i, 18);    'holes in compartment
         COLOR 14, 0
         PRINT " ";
         FOR j = 1 TO 6
          IF ASTROhealth%(j, 7) = i THEN PRINT USING "#"; j;  ELSE PRINT " ";
         NEXT j
         COLOR 12, 0
         LOCATE 10 + i, 53: IF Fire(i) > 0 THEN PRINT "FIRE"; : PRINT USING "#"; Fire(i) / 1000;  ELSE PRINT "     ";
         LOCATE 10 + i, 53: IF Fire(i) = 5000 THEN PRINT "ALARM";
         LOCATE 10 + i, 37
         IF var = 2 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 19) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "###.###"; ch(i, 19);    'oxygen variances
         IF var = 3 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 20) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "####.###"; ch(i, 20);    'carbon dioxide variance
         LOCATE 10 + i, 58
         IF var = 4 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 21) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "###.###"; ch(i, 21);    'water variance
         IF var = 5 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 22) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "####.#"; ch(i, 22);    'dust variance
         IF var = 6 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 23) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "###.#"; ch(i, 23);    'chemical hazards variance
         IF var = 7 AND cmp = i THEN clbk = 1 ELSE clbk = 0
         IF ch(i, 24) <> 0 THEN clfg = 12 ELSE clfg = 7
         COLOR clfg, clbk
         PRINT USING "###.#"; ch(i, 24);    'biohazard variance
        NEXT i
       
        COLOR 9, 0: LOCATE 19, 1: PRINT CHR$(18); ":           "; : COLOR 11, 0: PRINT "select compt";
        COLOR 9, 0: LOCATE 20, 1: PRINT CHR$(17); " "; CHR$(16); ":         "; : COLOR 11, 0: PRINT "select error";
        COLOR 9, 0: LOCATE 16, 1: PRINT "ENTER:   ";
        COLOR 9, 0: LOCATE 18, 1: PRINT "z x:         "; : COLOR 11, 0: PRINT "water="; : COLOR 14, 0: PRINT USING "##"; water;
        COLOR 9, 0: LOCATE 22, 30: PRINT "F8-F10:  ";
        COLOR 9, 0: LOCATE 21, 1: PRINT CHR$(241); " PgUp PgDn: "; : COLOR 11, 0: PRINT "changes";
        COLOR 9, 0: LOCATE 22, 55: PRINT "[]:    "; : COLOR 11, 0: PRINT "Star: "; : COLOR 14, 0: PRINT loc$(starN(star));
        COLOR 9, 0: LOCATE 24, 55: PRINT "<>=/:  "; : COLOR 11, 0: PRINT "flare:";
        COLOR 9, 0: LOCATE 22, 1: PRINT "Home End:    "; : COLOR 11, 0: PRINT "select door";
        COLOR 9, 0: LOCATE 23, 1: PRINT "*:           "; : COLOR 11, 0: PRINT "override";
        COLOR 9, 0: LOCATE 24, 1: PRINT "Ins Del M:   "; : COLOR 11, 0: PRINT "Opn Cls Malf";
        'COLOR 9, 0: LOCATE 24, 14: PRINT "M: "; : COLOR 11, 0: PRINT "malf";
        COLOR 7, 0

        LOCATE 2, 66: COLOR 11, 0: PRINT "Wind:   "; : COLOR 14, 0: PRINT USING "######"; WIND * 3.6;
        LOCATE 23, 30: COLOR 9, 0: PRINT "{ }:     "; : COLOR 11, 0: PRINT "Dust Adj: "; : COLOR 14, 0: PRINT USING "##"; dustX;
        LOCATE 19, 30: COLOR 9, 0: PRINT "q w:     "; : COLOR 11, 0: PRINT "Lightning:"; : COLOR 14, 0: PRINT USING "##"; lightning;
        LOCATE 20, 30: COLOR 9, 0: PRINT "d:       "; : COLOR 11, 0: PRINT "Discharge";
        LOCATE 21, 30: COLOR 9, 0: PRINT "( ):     "; : COLOR 11, 0: PRINT "Baro Adj:"; : COLOR 14, 0: PRINT USING "###"; delATM;
        locate 17, 30: color 9, 0: print "r R:     "; : color 11, 0: print "Reset gases";
        LOCATE 18, 30: COLOR 9, 0: PRINT "a s:     "; : COLOR 11, 0: PRINT "Temp Adj:"; : COLOR 14, 0: PRINT USING "###"; DELtemp - 7;
        LOCATE 24, 30: COLOR 9, 0: PRINT "f:       "; : COLOR 11, 0: PRINT "Compt Fire";
        LOCATE 25, 55: COLOR 9, 0: PRINT "c C:   "; : COLOR 11, 0: PRINT "RAD X"; : COLOR 14, 0: PRINT USING "#########"; cosmicFACTOR + 1;
        LOCATE 25, 30: COLOR 9, 0: PRINT "F1:      "; : COLOR 8 + (warn * 4), 0: PRINT "WARNING";

        COLOR 9, 0: LOCATE 1, 45: PRINT "OAT:      "; : COLOR 14, 0: PRINT USING "#####"; OAT - 273;
        LOCATE 2, 45: COLOR 9, 0: PRINT "RAD SHIELD: "; : COLOR 14, 0: PRINT USING "###"; MAGshield * 100;
        COLOR 9, 0: LOCATE 1, 17: PRINT "RAD:    "; : COLOR 14, 0: PRINT USING "#####.######"; RADout * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
        COLOR 9, 0: LOCATE 2, 17: PRINT "INSIDE: "; : COLOR 14, 0: PRINT USING "#####.######"; RADin * 1000000; : COLOR 9, 0: PRINT " "; CHR$(230); "S/s";
        LOCATE 24, 68: COLOR 14, 0: PRINT USING "########"; flare; : COLOR 11, 0: PRINT "X";
        clr = 8
        IF Asteroid = 1 THEN clr = 14
        IF Asteroid = 2 THEN clr = 12
        COLOR clr, 0: LOCATE 1, 72: PRINT "ASTEROID"; : LOCATE 22, 39: PRINT "ASTEROID";
        IF de(door) = 10 THEN COLOR 12, 0 ELSE COLOR 8, 0
        LOCATE 13, 10: PRINT door; "MALF ";
        COLOR 8 + (DOORoverride * 4), 0: LOCATE 15, 11: PRINT "OVERRIDE";
        IF ABS(ch(dr(door, 1), 0) - ch(dr(door, 2), 0)) > 10 THEN COLOR 12, 0 ELSE COLOR 8, 0
        LOCATE 14, 10: PRINT door; "PRESS";
        for j = 1 to 8
         if j = door then bkclr = 9 else bkclr = 0
         locate 13,j
         if de(j)=0 then color 8,bkclr:print chr$(1); else color 12,bkclr:print "M";
         locate 14,j
         if d(j)=0 then color 8, bkclr:print chr$(1);
         if d(j)=3 then color 14, bkclr:print "C";
         if d(j)=4 then color 12, bkclr:print "O";
        next j
        LOCATE 16, 11: COLOR 8 + (update * 4), 0 + (update * 5): PRINT "UPDATE";
        COLOR 8, 0
        LOCATE 17, 11: PRINT loc$(location);
        LOCATE 24, 78: COLOR 8 + (SGN(flareSIZE) * 4), 0: PRINT USING "#"; flareOCTANT; : PRINT ":"; : PRINT USING "#"; flareSIZE;

        LOCATE 18, 55: COLOR 9, 0: PRINT "F2 F3: "; : COLOR 11, 0: PRINT "Astro: ";
        FOR j = 1 TO 8
         fgclr = 6
         zz = 0
         FOR jj = 1 TO 6: zz = zz + ABS(ASTROhealth%(j, jj)): NEXT jj
         IF zz > 0 THEN fgclr = 4
         IF j = astro THEN fgclr = 14
         LOCATE 18, 69 + j: COLOR fgclr, 0
         PRINT CHR$(64 + j);
        NEXT j

        LOCATE 19, 55: COLOR 9, 0: PRINT "F4-F7: "; : COLOR 9, 0: PRINT "H  P  R  O  T  S";
        FOR j = 1 TO 6
         LOCATE 19, j * 3 + 60
         IF j = astroHval THEN bkclr = 9 ELSE bkclr = 0
         fgclr = 10
         IF ABS(ASTROhealth%(astro, j)) = 3 THEN fgclr = 12
         IF ABS(ASTROhealth%(astro, j)) = 2 THEN fgclr = 14
         IF ASTROhealth%(astro, j) < 0 THEN zz$ = "- " ELSE zz$ = "0 "
         IF ASTROhealth%(astro, j) > 0 THEN zz$ = "+ "
         COLOR fgclr, bkclr: PRINT zz$;
        NEXT j
        COLOR 8 + (warn * 4), 0
        LOCATE 20, 55: PRINT eecomwarning1$;
        LOCATE 21, 55: PRINT eecomwarning2$;

        RETURN




2000    'IF ERL = 80 THEN RESUME 81
        'IF ERL = 500 THEN CLOSE #1: RESUME 500
        'IF ERL = 660 THEN CLOSE #1: RESUME 660
        'IF ERL = 8000 THEN CLOSE #1: RESUME 8103
        'IF ERL = 8104 OR ERL = 8004 THEN CLOSE #1: RESUME 8003
        CLS
        PRINT "line="; ERL
        PRINT "error="; ERR
        z$ = INPUT$(1)
        END

6000    FOR i = 1 TO 6
         Fire(i) = 0
         FOR j = 18 TO 24
          ch(i, j) = 0
         NEXT j
        NEXT i
        Asteroid = 0
        WIND = 0
        dustX = 0
        lightning = 0
        DELtemp = 7
        FOR i = 1 TO 8
         de(i) = 0
        NEXT i
        flare = 1
        RETURN



8000    tblock = TIMER
8081    OPEN "R", #1, pathname$ + "GASMC.RND", 82
        inpSTR=space$(82)
        k=k+1
        get #1, 1, inpSTR
        close #1
        chkCHAR1$=left$(inpSTR,1)
        chkCHAR2$=right$(inpSTR,1)
        if chkCHAR1$=chkCHAR2$ then 8082
        if k<5 then 8081
        locate 25,1
        color 14,0
        print "MC File Error    ";
        goto 8104
8082    k=74
        FOR i = 1 TO 8
         ASTROstat(i) = cvi(mid$(inpSTR, k,2)):k=k+2
        NEXT i
       
8104    k=1
8102    OPEN "R", #1, "OSBACKUP.RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if len(inpSTR$) <> 1427 then 8109
        IF ORBITversion$ = "XXXXXXX" THEN RUN "gassimv" 
        IF ORBITversion$ <> "ORBIT5S" THEN 8109
        if chkCHAR1$=chkCHAR2$ then 8107
        k=k+1
        if k<4 then 8102
        tttt = TIMER + .8
        goto 8109

8107    k=89
        year = cvi(mid$(inpSTR$,k,2)):k=k+2
        day = cvi(mid$(inpSTR$,k,2)):k=k+2
        hour = cvi(mid$(inpSTR$,k,2)):k=k+2
        min = cvi(mid$(inpSTR$,k,2)):k=k+2
        sec = cvd(mid$(inpSTR$,k,8))
        k=2+15
        eng = cvs(mid$(inpSTR$,k,4)):k=k+8+18
        Sangle = cvs(mid$(inpSTR$,k,4)):k=k+6+6+12+16+22+6
        oldWIND = WIND
        Wind = cvs(mid$(inpSTR$,k,4)):k=k+4+8
        AYSE = cvi(mid$(inpSTR$,k,2)):k=k+2
        MAGshield = cvs(mid$(inpSTR$,k,4)):k=k+4+14+28
        FOR i = 1 TO 34
         x(i) = cvd(mid$(inpSTR$,k,8)):k=k+8
         y(i) = cvd(mid$(inpSTR$,k,8)):k=k+24
        NEXT i
        
        IF WIND > 500 THEN WIND = 500
        WIND = CINT(WIND)
        IF oldWIND <> WIND THEN GOSUB 660

8109    newtime# = sec + (60# * min) + (3600# * hour) + (86400# * day) + (31536000# * year)
        IF oldtime# = -1 THEN DELtime = 0 ELSE DELtime = newtime# - oldtime#
        IF DELtime < 0 THEN DELtime = 0
        LOCATE 25, 1
        IF DELtime = 0 THEN COLOR 12, 0: timealarm = timealarm + 1 ELSE COLOR 10, 0: timealarm = 0
        PRINT USING "####"; year; : PRINT ":";
        PRINT USING "###"; day; : PRINT ":";
        PRINT USING "##"; hour; : PRINT ":";
        PRINT USING "##"; min; : PRINT ":";
        PRINT USING "##"; sec;
        IF timealarm > 5 THEN timealarm=6: 'beep
        oldtime# = newtime#
        'RETURN

8005    cosmic = 2.55E-09 * (.97 + (.06 * RND))
        cosmic = cosmic * (1 + cosmicFACTOR)
        location = 0
        atm = 0
        block = 1
        difx = x(28) - x(starN(star))
        dify = y(28) - y(starN(star))
        Rsun# = (SQR((dify ^ 2) + (difx ^ 2))) / 1000
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        BLOCKangle = ABS(angle - Sangle)
        IF BLOCKangle > 3.1415926535# THEN BLOCKangle = 6.283185307# - BLOCKangle
        RADz = solar
        IF BLOCKangle > 2.9 THEN BLOCKangle = 10.35 * (BLOCKangle - 2.9) / .25 ELSE BLOCKangle = 1
        RADz= 7.9E+18 / (Rsun# ^ 3.5)
        RADz = RADz + ((7.7E+07 / (Rsun# ^ 2)) * flare)
       
8007    RADout = RADz
        RADz = RADz / BLOCKangle
        FOR i = 1 TO 34
         IF i = 28 THEN 8006
         IF i = 32 THEN 8006
         dist = SQR((x(i) - x(28)) ^ 2 + (y(i) - y(28)) ^ 2)
         DISTi = (dist - RAD(i)) / 1000
         IF dist < (thickness(i) * 1000) + RAD(i) THEN location = i: ATMdist = DISTi
         IF i = 3 AND DISTi < 38000 THEN GOSUB 9200
         IF i = 5 AND DISTi < 1500000 THEN GOSUB 9300
         IF i = 6 AND DISTi < 500000 THEN GOSUB 9400
         IF i = 7 AND DISTi < 360000 THEN GOSUB 9500
         IF i = 8 AND DISTi < 310000 THEN GOSUB 9600
         IF i = 24 AND DISTi < 38000 THEN GOSUB 9200
         GOSUB 9000
8006    NEXT i
        'LOCATE 13, 1: PRINT atm, location;                
        LOCATE 23, 55: IF block = 1 THEN COLOR 14, 0: PRINT "Stellar rads not blocked ";  ELSE COLOR 10, 0: PRINT "Stellar rads blocked     ";
        RADz = RADz * block
        RADout = RADout * block
        RADz = RADz + cosmic
        RADout = RADout + cosmic
        RADz = RADz + RADc
        RADout = RADout + RADc
        IF location = 0 THEN atm = 0 ELSE atm = refDEN(location) * (2.71828 ^ (-1 * ATMdist / refALT(location)))
        IF atm < 0 THEN atm = 0
        RADz = RADz / (1 + atm)
        RADout = RADout / (1 + atm)
        newRAD = (RADz + oldRAD) / 2
        oldRAD = RADz
        RADin = newRAD
        shieldIN = .1
        shieldOUT = .4
        IF AYSE = 150 THEN shieldIN = shieldIN * .4
        shieldIN = shieldIN / (1 + (MAGshield / .0825))
        shieldOUT = shieldOUT / (1 + (MAGshield / .275))
        RADin = RADin * shieldIN
        FOR i = 1 TO 8
         IF ASTROstat(i) = 0 THEN shield = shieldIN ELSE shield = shieldOUT
         ASTROrad(i) = ASTROrad(i) + (newRAD * shield * DELtime)
        NEXT i
        if OLDlocation<>location then gosub 660
        OLDlocation = location
        RETURN
       

        'Solar Radiation Blocked by Another Object
9000    difx = x(i) - x(starN(star))
        dify = y(i) - y(starN(star))
        Rblock# = SQR((dify ^ 2) + (difx ^ 2))
        IF Rblock# >= Rsun# * 1000 THEN 9100
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        angleBLOCK = angle
       
        difx = x(28) - x(i)
        dify = y(28) - y(i)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF R > RAD(i) * 6 THEN 9100
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Ahbs = angle - angleBLOCK
        IF Ahbs > 3.1415926535# THEN Ahbs = -6.283185307# + Ahbs
        IF Ahbs < -3.1415926535# THEN Ahbs = 6.283185307# + Ahbs
        Ahbs = ABS(Ahbs)
        Rx = R * SIN(Ahbs)
        Rcrit = RAD(i) - ((R - RAD(i)) / 5)
        IF Rcrit > Rx THEN block = 0
        'Roff = R * SIN(3.1415926535# - Ahbs)
        'Rcrit = (1.2 * RAD(i)) - (.2 * R)
        'IF Roff < Rcrit THEN block = 0
9100    RETURN
       
        'earth
9200    m1 = 3000
        s1 = 540
        m2 = 20000
        s2 = 3990
        a3 = .111
        b3 = .61
        az = (DISTi - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        b = (DISTi - m2) ^ 2
        b = b / (2 * s2 * s2)
        b = 2.81 ^ (-1 * b)
        b = b / (2.5 * s2)
        b = b * b3
        RADc = az + b
        IF DISTi < 3000.13 THEN RADz = RADz / (-1 * LOG(RADc)): cosmic = cosmic / (-1 * LOG(RADc)): RADout = RADout / (-1 * LOG(RADc))
        RETURN

        'jupiter
9300    m1 = 421000
        s1 = 98000
        m2 = 671000
        s2 = 165100
        a3 = 400
        b3 = 270
        az = (DISTi - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        az = az * a3
        b = (DISTi - m2) ^ 2
        b = b / (2 * s2 * s2)
        b = 2.81 ^ (-1 * b)
        b = b / (2.5 * s2)
        b = b * b3
        RADc = az + b
        IF DISTi < 3000.13 THEN RADz = RADz / (-1 * LOG(RADc)): cosmic = cosmic / (-1 * LOG(RADc)): RADout = RADout / (-1 * LOG(RADc))
        RETURN

        'saturn
9400    m1 = 251000
        s1 = 52000
        a3 = 42.75
        az = (DISTi - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        RADc = az * a3
        IF DISTi < 3000.13 THEN RADz = RADz / (-1 * LOG(RADc)): cosmic = cosmic / (-1 * LOG(RADc)): RADout = RADout / (-1 * LOG(RADc))
        RETURN

        'uranus
9500    m1 = 181000
        s1 = 38000
        a3 = 15.06
        az = (DISTi - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        RADc = az * a3
        IF DISTi < 3000.13 THEN RADz = RADz / (-1 * LOG(RADc)): cosmic = cosmic / (-1 * LOG(RADc)): RADout = RADout / (-1 * LOG(RADc))
        RETURN


        'neptune
9600    m1 = 151000
        s1 = 34000
        a3 = 8.14
        az = (DISTi - m1) ^ 2
        az = az / (2 * s1 * s1)
        az = 2.81 ^ (-1 * az)
        az = az / (2.5 * s1)
        RADc = az * a3
        IF DISTi < 3000.13 THEN RADz = RADz / (-1 * LOG(RADc)): cosmic = cosmic / (-1 * LOG(RADc)): RADout = RADout / (-1 * LOG(RADc))
        RETURN

9700    'Store Astronaut Radiation Data
        IF EflagNEW = 0 THEN 9760
        Eflag = EflagNEW
        OPEN "I", #2, "Eflag.dat"
        FOR i = 1 TO EflagNEW
         INPUT #2, z$
         FOR ii = 1 TO 8
          INPUT #2, ASTROrad(ii)
         NEXT ii
        NEXT i
        CLOSE #2
        GOTO 9790


9760    FOR i = 1 TO 8
         ASTROrad(i) = 0
        NEXT i
9790    RETURN


         


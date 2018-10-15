819     OPEN "R", #1, "ORBITSSE.RND", 254
        inpSTR$=space$(254)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 254 then locate 25, 1:color 12:print "ENG telem";:goto 812
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=mid$(inpSTR$,210,1)
        if chkCHAR1$=chkCHAR2$ then 818
        k=k+1
        if k<3 then 819
        locate 25, 1:color 12:print "ENG telem*";
        goto 812


818     ufo1 = 1
        activeOLD=active
        active=cvi(mid$(inpSTR$,211,2))':locate 6,40:print active;
        if active = 0 and activeOLD=1 and activeAYSE=1 then AYSE=0
        if active=0 then Px=1e50 else Px=cvd(mid$(inpSTR$,213,8))
        if active=0 then Py=1e50 else Py=cvd(mid$(inpSTR$,221,8))
        Vx=cvd(mid$(inpSTR$,229,8))
        Vy=cvd(mid$(inpSTR$,237,8))
        locate 1,40:print Px;
        locate 2,40:print Py;
        locate 3,40:print Vx;
        locate 4,40:print Vy;
        activeAYSE=cvi(mid$(inpSTR$,245,2))
        HSangle=cvd(mid$(pirateSTR$,347,8))
        if activeAYSE<>150 then 812
        goto 812
812     z$=inkey$
        if z$<>"" then end
        goto 819
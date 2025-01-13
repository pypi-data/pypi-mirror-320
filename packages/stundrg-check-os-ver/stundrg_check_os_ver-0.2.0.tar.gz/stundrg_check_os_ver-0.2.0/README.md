# stundrg-check-os-ver
- Detects and outputs the os version.



                                            :                              
                                           :;:                             
                                          .;+;                             
               .                     .;:..;;;;                             
               :            .:       :;;+:;xx+:                            
              .+:           .;  .::  :;++:;;;+XX++;.                       
              :x+      :    :;  .;;;;;;xX+;;;+XXXXXXx+;:                   
              .xx.     :;..:;++++XXX+++;xx;;++XXXXX$XXxx:                  
             .:xx+..:..;+xXxxxxX$XXX+;;..:;;;+xXXXXxxx+;+                  
             ..;++. ;;XXX+X$$$&&$XXx+;:::::;;+++XxXxxX;;;+.                
               :+X$+XX$++;;++X$$XXX;.;;;;;;;;++++X$$X+;;:;++:              
                ;X$xX$+x$$$+X$$$X$XX;XXX++X+++x++xX$X+;;::: ..             
                 :;XXXx+$X$$$$X$$$$$XXXXXxx+++++XX$XXx+;:::::. ;.          
                  .:;XX+;+X$X$XXXX$XX$X$$XXx++++XX+xXX;;;:::+;;;;          
                     ;;;.:X$XXXX+;xX$$$XX$$$X++++xxX+X++xx+:;;;;;:         
                         :+X$xX+;+++XX+X$$XxX.;;++XXXx:;xxx;x++;x:         
                         :+Xx;;.+++$++X$$$$$$x  X$&$$$;;xxXxx+;;;.         
                        .;X:;;+;:X+xxX$$$$$$X   X$$$$X;:+xx$xXx++;         
                        .;:x++X$XXX$$XX$$x;:.   :X++xX++;;:+$$++x:         
                         ::+$X+;x$X$$XX$Xx+.    :+x;+XX$& ..;+++;          
                    .:;++++;:x+XX++XX$XX$$$x  . :xx++XX$&:..++++.          
                    ::X$$Xx:+$$$X+:;+XX$X$$$$$$X.+;+xxX$$X::+++:           
                   :.:X$$XXx$$$$$$XXX$&$X$$X$&$$X;;xxxX$XX;+++;            
                  :..+XXX$&$X;$XXX$xx$$$$$;;;x$$x+++Xx$$$X;++;.            
                 .::;XXx$$XX++$$XXXXx$$&$;:;;;++++++xXX$X;++:;             
                 ;:;XX+;X;;;+X&$$XXXX$Xx+x;;;;X++x$$$$$XX++:.;             
     ::;;.     :;::xXx+;+XXXXXX++xXXXXX+;;;;;.+$X+X$$$$XX;.:;:             
      :+Xx;   .;.::+X++xX++++xX;;x+xX$XXXx+;;:.x$XX$$$$XXx+X;              
       .+Xx+: :::;;;+XXXx+xXXXX::Xx+XXXX++++;;..XXXX$$$$X+;X:              
        .:XX+XX;XXX+XXXXxxX$XX$;.xX&&&.  :;x++;.:XXX$$$X+;;X               
          :XX++XXXXxx+x;.;$$$$$+.+xX&X    :;+Xx:::XXx:;:;;++               
           :+XX+;XXXxXX$$$$$$$$X.;xX&+     .::$X++;X:+.;;+$:               
           ::;+xXx;XXX+X$$$$$$$$::x+;.    ::;::XXx+x+x+XX$$;               
         ..:X+X$$+xXX$X$X$$$$$$X;:x+:     ++XX+:+;++$X$X$$$;               
        ..;X$$$$XxXXX$$$$$XxxxXX++:;:     :X$XXXXxx+X$$$$$X                
       ..;xXX$$$X:... ..x$$++xXXx:          +$$$$$XxxX$$$XX.               
      ..;+xxxXXx.     .:+XX$+xxxX$$+         .:xX$XXXX$$$X+:               
    ..:+++++++;      :X$$$$$;+xxX$$X+            +;XX$$XXXx;               
   :.;XXxxx++.      +$X$XX$X;X$$$$$XX:            ::XxXX$XX$X.             
  ..x$$XXXX+.        :$$XXX+$$$$XX$XX;            .;++x++++X$X+            
 ..:$$$$$$;    ::::..:$XXX+X$XX$$XX+;:            ;+++x+;;;x$$XX;          
 . ;X$$$$$ ...;x+;+x+++++XX$$$$x;.               ;;; ;xx++xX$$XXX+         
 ::+;$X$X;.::::.;XXx;+xX$$$$$X+                 :;; :X$$$$XXXXXX$X:        
.:+:;+:X:;++:.:++x++xX$$XXXXx;                  ;;;xX$XXXXXXXXXXXx+        
:..+:.x  + :.++;:+XXXXXX+;                      ;xX$X+;;;;++++XxXX::;:     
   ..:      +:    :+;+xx:.                       ;xx;++x+++XXX++++++X;;.   
            :     :..;+;                       :+;;+xxXX+;x+X$XXx+xx:...:  
                   .:;++:                    .::..;XXXXX++;.+xX$XXX+:::..: 
                     ::::.                   :.:;++XXXXX+x..:+xxxxXx++++:: 
                                             ::++++x++;:+x:.:+++  :;;::;+;:
                                             :;+;;;:.    ::..++         .+;
                                             .;:           :.+:           .
                                              :             .;             
 :.:...: .  :.:.:::.::. . .::::::. .  .. .                                 
.::;:;:;:;..::;:;+;;::;::.:+;;;:.:::..:::::.    

### Use

```python
$ pip install stundrg-check-os-ver
$ python
>>> from stundrg_check_os_ver.hi import hi
>>> hi()
```

### Development environment setting
```bash
# install PDM
# git clone ...
$ source .venv/bin/activate
# pdm install
# $ vi ...

# TEST
$ pdm install
$ pdm test
$ pip install .

$ git add<FILE_NAME>
$ git push
$ pdm publish
```


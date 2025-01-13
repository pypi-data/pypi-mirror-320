# stundrg-check-os-ver
- Detects and outputs the os version.

                                  ..                       
                                 .;;                       
                             .:. :;;.                      
            :         .:     :;;;+x+:                      
           :;.        :: .;:.:+x;;;+XXX+:.                 
           :x:    ::  ;;:;++x+;+X;;+XXXX$Xx+.              
           :x+.   ;+xx+xxXXX+;;::;;;+XXXXx+++              
           :;+::;xX+x$$$&$$X+;::::;+++XXXX+;;+.            
            :x$X$X+X+;;X$XX+:++;;+;++++xXX;;:;;;:          
             :XXXx+$$$$$$$$$$$XXxx+xxxx$XX+;:::.           
              .:+X+;x$$XXXX$X$$$Xx++;+X+XX+;;::+;;;        
                .::.+X$XX+;+X$XxX$Xx+++xX+x+xx;;;;;;       
                   .:+X;:++xXxx$$$$X..+$$$+;xx+x+++.       
                   :++;+;;xxxX$$$$$; .$$$$x:xxXxX++;       
                   ::++x$XX$$XX$x;.   ;++xx+;;:X$+x:       
                  ..:+X+;+XX$X$$Xx:   ;x++X$&..;++;        
                :+XXx;;X$X;;+XXX$$X++;;++xX$$;:+++:        
               :.+$$Xx$$$$$XX$&X$$$&$X+;xxX$Xx;++;         
              :.;xXX$$x+XXXXx$$$X;;+XX+++xX$$+;;;.         
             .::xX;XXXX$$$XXX$$X+:;;;+xXxXXXX+;.:          
    ...     :::xX+;+XXXX$XxXXXx;;;;:+$xX$$$XX;.::          
    .;Xx:  .:::+X+xX+++x+;xxX$XXx+;:.xXX$$$$X+x;           
      :XX;.:;+;+XXXxxXXX;:XxXxx+;;+;::XXX$$$X;x:           
       .+X+XXXX++xX;+XXXx:+X&$  .;+X+::XX+;:+;+.           
        .+Xx++XXXX$$$$$$X:;X&+    ::X+;;X::;;++            
        .:;+XX;XX+X$$$$$$:;x:    ::::xX+++XXX$x.           
       .:XXX$XXXX$$$$XXXX+;+;    +$XX;+++$$$$$+            
      .:xX$$$x;;;;;X$++xX+:       ;$XX$X++X$$X;            
     .;+xxXX+     .+X$xxxX$x:       :X$$XXX$$X;            
   ..++++++:    :x$$$$++X$$$x.        :;xX$XXXx.           
  .:XXXXx;.     ;$XXXX+$$$XXX+         .:+xX$XX$+.         
 .:$$$$X;   ... .X$XxX$$X$$X+:         :;+++;;+$$X;        
 .;X$$$$..:++;+x+++xX$$$X;.           :;;:+xxxX$$XX+       
 :+:XxX::;...+X;+XX$$XXx:            .;;.x$$XXXXXX$X;      
:::+:;.+;:;+++xxX$Xx+;:              .+X$X+;;;++XXXX:..    
  ..:    :;   :++xX:.                 :+x;++++xXX++++x+;.  
              ..:+;                  ;+++XXX+++x$XXxX;.... 
               .:;;;.              ...:;XXXX++.;xXXXX++;:: 
                                   ..+++xx+;++.:++;.;+;:+;:
                                   .;+;;:.   ::.+;       ;;
                                   .;.         .+.         
                                                .          
:;;;;;;;.::+;+;;;;:::+;+;:::::::;:.                        
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
Username:__token__
password : Token
```


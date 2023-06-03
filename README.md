# VPadClient4Geek
这是一个基于Python的编程式VPad客户端，除了提供基本的VPad客户端功能外，还提供了一个简易的VPad服务器框架，该框架只解析VPad协议的消息，你可以用它做很多有趣的事，比如建立一个真实VPad服务器与客户端之间的中间层（类似反向代理），然后，世界就是你的了，毕竟：
> **计算机世界中的任何难题都可以通过添加一个中间层解决**  
> Any problem in computer science can be solved by another layer of indirection.

但是...

> 除了中间层太多的问题  
> except for the problem of too many layers of indirection.

中间层太多会严重影响效率，VPad是一个效率优先的软件，所以，请在效率和创意之间进行权衡！

下面提供了两个使用示例：

示例|介绍|其它技术
:-|:-|:-
[251.py][./251.py]|连接到VPadClient，并简单的发送一个251和弦|无
[sequencer.py][./sequencer.py]|提供一个步进音序器（Step Sequencer）。该脚本会建立一个反向代理，并将客户端的消息转换成步进音序器上按钮的激活与关闭，这样，我们可以把客户端当成一个步进音序器来用。|使用curses在终端上构建GUI

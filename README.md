## RIFTGUN
*A new module for providing remote support on discord bots*

### What is it?
*RiftGun*, commonly known as "Rifter", is a python module that
you can load into your discord bots to spy on channels.

#### I DO NOT CONDONE USE OF THIS FOR PRIVACY INVASION, OR UNETHICAL USES!
This module was designed as an easy way for us to remotely provide 
support and investigate servers that we thought broke DragDev Studios'
terms of service. While we can't stop you, we advise you don't use this 
to do any "spying" or otherwise indecent operations

---
### Installation:
From **git**:
```shell script
$ pip install git+https://github.com/dragdev-studios/riftgun
```

then to load it into the bot, simply add this before `bot.run()`:
```python
bot.load_extension("riftgun")
```

When you successfully load the module, the bot will create a file where you are running your bot called `rifts.min.json`.
If this does not already exist, or is broken, it will be created.
Otherwise, it will be loaded instead.
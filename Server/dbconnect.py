import mongoengine as me

class keycollection(me.Document):
    rand = me.StringField(unique=True)
    key = me.StringField()
    timestamp = me.FloatField()

    @classmethod
    def query(cls, **kw):
        return cls.objects(**kw)

class session(me.Document): # connection
    identity = me.StringField(unique=True)
    token = me.StringField() # this acts as a salt in encryption & connect
    key = me.StringField() # key for encryption

    @classmethod
    def query(cls, **kw):
        return cls.objects(**kw)
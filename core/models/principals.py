from core import db
from core.libs import helpers


class Principal(db.Model):
    __tablename__ = 'principals'
    id = db.Column(db.Integer, db.Sequence('principals_id_seq'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Principal %r>' % self.id

    # def __repr__(self):
    #     # return str(self.__dict__)
    #     return f'<Principal(id={self.id}, user_id={self.user_id}, created={self.created_at}, updated={self.updated_at})>'
    
    # def __repr__(self):
    #     fields = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
    #     return str(fields)

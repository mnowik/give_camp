from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class BaseMixin(object):
    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)


class User(BaseMixin, db.Model):
    username = db.Column(db.String(80), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Campaign(BaseMixin, db.Model):
    name       = db.Column(db.String(120), nullable=False)
    content    = db.Column(db.String(300), nullable=True)
    min_amount = db.Column(db.Integer, nullable=True)
    max_amount = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Name %r, Max Amount %s>' % (self.name, self.max_amount)

    def all_matches_qs(self):
      """ Retrieve all matches for a given Campaign"""
      return Match.query.filter(Match.campaign_id==self.id)

    def all_open_matches_qs(self):
      """ Retrieve all none over matches for a given Campaign"""
      return self.all_matches_qs().filter(Match.is_over==False)


class Donation(BaseMixin, db.Model):
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    amount      = db.Column(db.Integer, nullable=False)

    def create(self, user_id, camp_id, amount):
      d = Donation(user_id=user_id, campaign_id=camp_id, amount=amount)
      db.session.add(d)
      db.session.commit()
      return d

    def __repr__(self):
        return '<UserID %r, CampaignID %s, Amount %s>' % (self.user_id, self.campaign_id, self.amount)


class Match(BaseMixin, db.Model):
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    max_amount  = db.Column(db.Integer, nullable=False)
    type_match  = db.Column(db.String(80), nullable=False)
    is_over     = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<UserID %r, CampaignID %s, IsOver %s>' % (self.user_id, self.campaign_id, self.is_over)

    def set_is_over(self):
      self.is_over=True
      db.session.commit()

    def get_current_amount(self):
      dms = DonationMatch.query.filter(DonationMatch.match_id==self.id).all()
      return reduce(lambda prev, curr: prev+curr.amount, dms, 0)
    
    def get_remaining_amount(self):
      return self.max_amount - self.get_current_amount()

    def how_much_match(self, amount):
      if self.is_over:
        return 0
      return min(amount, self.get_remaining_amount())


class DonationMatch(BaseMixin, db.Model):
    match_id    = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    type_match  = db.Column(db.String(80), nullable=False)
    amount      = db.Column(db.Integer, nullable=False)

    def create(self, match_id, donation_id, type_match, amount):
      dm = DonationMatch(match_id=match_id, donation_id=donation_id, type_match=type_match, amount=amount)
      db.session.add(dm)
      db.session.commit()
      return dm

    def __repr__(self):
      return '<MatchID %r, Amount %s>' % (self.match_id, self.amount)




from model import *

db.create_all()
db.drop_all()

admin = User(username='admin', email='admin@example.com')
c = Campaign(name="Hillary's campaign", content="2017 elections", max_amount=10000)
db.session.add(admin)
db.session.add(c)
db.session.commit()


user_id = User.query.first().id
c_id = Campaign.query.first().id

# Match
m = Match(user_id=user_id, campaign_id=c_id, max_amount=3000, type_match="1-1")
db.session.add(m)
db.session.commit()

# Donation
d = Donation(user_id=user_id, campaign_id=c_id, amount=500)
db.session.add(d)
db.session.commit()


# Donation Match
match_id = Match.query.first().id
don_id = Donation.query.first().id
dm = DonationMatch(match_id=match_id, donation_id=don_id, type_match="1-1", amount=500)
db.session.add(dm)
db.session.commit()
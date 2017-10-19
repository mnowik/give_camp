from flask import request, Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from model import db, User, Campaign, Donation, DonationMatch

#######################
#### configuration ####
#######################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# db
db.init_app(app)


@app.route('/donate', methods=["GET", "POST"])
def donate():
    if request.method == "GET":
      return render_template('donate.html')
    else:
      # user_id = request.user.id if request.user else None
      user_id = None
      camp_id = request.form.get('campaign_id')
      amount  = request.form.get('amount', 0)

      # campaign handler
      camps = Campaign.query.filter(Campaign.id==camp_id).all()
      if len(camps) != 1:
        return render_template('donate.html', error="No Campaign Matching")
      camp = camps[0]

      # create donation
      donation = Donation().create(user_id, camp_id, amount)
      
      # create donation matches
      open_matches = camp.all_open_matches_qs().all()

      for om in open_matches:
        match_amount = om.how_much_match(amount)
        dm = DonationMatch().create(om.id, donation.id, om.type_match, match_amount)
        if om.get_remaining_amount() <= 0:
          # set Match to is_over if max amount is reached 
          om.set_is_over()

      camp_curr_amount = camp.max_amount
      return render_template('donate.html', camp_curr=camp_curr_amount)
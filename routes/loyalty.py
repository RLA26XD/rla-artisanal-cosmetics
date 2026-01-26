"""
Loyalty program routes
"""
from flask import Blueprint, render_template, session, jsonify, request
from models.user import User, LoyaltyAccount
from models import db

loyalty_bp = Blueprint('loyalty', __name__)


@loyalty_bp.route('/rewards')
def rewards():
    """
    My Rewards page showing loyalty points and tier progress.
    For demo purposes, uses session-based mock user.
    """
    # In a real app, get user_id from authenticated session
    # For demo, we'll create a mock loyalty account
    
    # Get or create demo user
    demo_user = User.query.filter_by(email='demo@rlacosmetics.com').first()
    if not demo_user:
        demo_user = User(
            email='demo@rlacosmetics.com',
            name='Demo User',
            city='Mumbai',
            state='Maharashtra'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()
        
        # Create loyalty account
        loyalty = LoyaltyAccount(
            user_id=demo_user.id,
            points_balance=2500,
            lifetime_points=2500
        )
        loyalty.update_tier()
        db.session.add(loyalty)
        db.session.commit()
    
    loyalty_account = LoyaltyAccount.query.filter_by(user_id=demo_user.id).first()
    if not loyalty_account:
        loyalty_account = LoyaltyAccount(
            user_id=demo_user.id,
            points_balance=2500,
            lifetime_points=2500
        )
        loyalty_account.update_tier()
        db.session.add(loyalty_account)
        db.session.commit()
    
    return render_template(
        'loyalty/rewards.html',
        user=demo_user,
        loyalty=loyalty_account,
        loyalty_data=loyalty_account.to_dict()
    )


@loyalty_bp.route('/api/add-points', methods=['POST'])
def add_points():
    """
    API endpoint to add loyalty points.
    In production, this would be called after a successful purchase.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    if not user_id or points <= 0:
        return jsonify({'error': 'Invalid request'}), 400
    
    loyalty_account = LoyaltyAccount.query.filter_by(user_id=user_id).first()
    if not loyalty_account:
        return jsonify({'error': 'Loyalty account not found'}), 404
    
    loyalty_account.add_points(points)
    
    return jsonify({
        'success': True,
        'loyalty_data': loyalty_account.to_dict()
    })


@loyalty_bp.route('/api/redeem-points', methods=['POST'])
def redeem_points():
    """
    API endpoint to redeem loyalty points.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    if not user_id or points <= 0:
        return jsonify({'error': 'Invalid request'}), 400
    
    loyalty_account = LoyaltyAccount.query.filter_by(user_id=user_id).first()
    if not loyalty_account:
        return jsonify({'error': 'Loyalty account not found'}), 404
    
    if loyalty_account.redeem_points(points):
        return jsonify({
            'success': True,
            'message': f'Successfully redeemed {points} points',
            'loyalty_data': loyalty_account.to_dict()
        })
    else:
        return jsonify({
            'error': 'Insufficient points balance'
        }), 400

"""
Loyalty program routes
"""
from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import User, LoyaltyAccount
from models import db

loyalty_bp = Blueprint('loyalty', __name__)


@loyalty_bp.route('/rewards')
@login_required
def rewards():
    """
    My Rewards page showing loyalty points and tier progress.
    """
    # Get or create loyalty account for the current user
    loyalty_account = LoyaltyAccount.query.filter_by(user_id=current_user.id).first()
    
    if not loyalty_account:
        # Create loyalty account if it doesn't exist
        loyalty_account = LoyaltyAccount(
            user_id=current_user.id,
            points_balance=0,
            lifetime_points=0
        )
        loyalty_account.update_tier()
        db.session.add(loyalty_account)
        db.session.commit()
    
    return render_template(
        'loyalty/rewards.html',
        user=current_user,
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

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'order-service'}), 200

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT o.*, 
                   json_agg(json_build_object(
                       'product_id', oi.product_id,
                       'quantity', oi.quantity,
                       'price', oi.price
                   )) as items
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT o.*, 
                   json_agg(json_build_object(
                       'product_id', oi.product_id,
                       'quantity', oi.quantity,
                       'price', oi.price
                   )) as items
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.id = %s
            GROUP BY o.id
        ''', (order_id,))
        order = cur.fetchone()
        cur.close()
        conn.close()
        
        if order:
            return jsonify(order), 200
        return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create order
        cur.execute(
            '''INSERT INTO orders (customer_email, total_amount, status)
               VALUES (%s, %s, %s) RETURNING id''',
            (data.get('customer_email', 'guest@example.com'), 
             data['total_amount'], 
             'pending')
        )
        order_id = cur.fetchone()['id']
        
        # Create order items
        for item in data['items']:
            cur.execute(
                '''INSERT INTO order_items (order_id, product_id, quantity, price)
                   VALUES (%s, %s, %s, %s)''',
                (order_id, item['product_id'], item['quantity'], item['price'])
            )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'order_id': order_id, 
            'message': 'Order created successfully',
            'status': 'pending'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            'UPDATE orders SET status = %s WHERE id = %s',
            (data['status'], order_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Order status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE orders SET status = 'cancelled' WHERE id = %s AND status = 'pending'",
            (order_id,)
        )
        
        if cur.rowcount == 0:
            return jsonify({'error': 'Order cannot be cancelled'}), 400
            
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Order cancelled successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

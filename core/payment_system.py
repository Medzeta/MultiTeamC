"""
Payment System
Handles Stripe/PayPal payment integration
"""

import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from .debug_logger import debug, info, warning, error

class PaymentSystem:
    """
    Payment integration system
    Supports Stripe and PayPal
    """
    
    # Tier pricing (monthly)
    TIER_PRICING = {
        "basic": 0.00,
        "standard": 9.99,
        "professional": 29.99,
        "enterprise": 99.99,
        "ultimate": 199.99
    }
    
    def __init__(self, provider="stripe"):
        """
        Initialize payment system
        
        Args:
            provider: Payment provider (stripe or paypal)
        """
        self.provider = provider
        self.stripe_api_key = None
        self.paypal_client_id = None
        
        info("PaymentSystem", f"Payment system initialized with provider: {provider}")
    
    def configure_stripe(self, api_key: str, publishable_key: str):
        """
        Configure Stripe integration
        
        Args:
            api_key: Stripe secret API key
            publishable_key: Stripe publishable key
        """
        try:
            import stripe
            stripe.api_key = api_key
            self.stripe_api_key = api_key
            self.stripe_publishable_key = publishable_key
            
            info("PaymentSystem", "Stripe configured successfully")
            return True
        except ImportError:
            error("PaymentSystem", "Stripe library not installed. Run: pip install stripe")
            return False
        except Exception as e:
            error("PaymentSystem", f"Error configuring Stripe: {e}")
            return False
    
    def configure_paypal(self, client_id: str, client_secret: str):
        """
        Configure PayPal integration
        
        Args:
            client_id: PayPal client ID
            client_secret: PayPal client secret
        """
        try:
            import paypalrestsdk
            
            paypalrestsdk.configure({
                "mode": "sandbox",  # Change to "live" for production
                "client_id": client_id,
                "client_secret": client_secret
            })
            
            self.paypal_client_id = client_id
            
            info("PaymentSystem", "PayPal configured successfully")
            return True
        except ImportError:
            error("PaymentSystem", "PayPal SDK not installed. Run: pip install paypalrestsdk")
            return False
        except Exception as e:
            error("PaymentSystem", f"Error configuring PayPal: {e}")
            return False
    
    def get_tier_price(self, tier: str) -> float:
        """Get price for a tier"""
        return self.TIER_PRICING.get(tier.lower(), 0.00)
    
    def create_payment_intent_stripe(self, tier: str, email: str, metadata: Dict = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create Stripe payment intent
        
        Args:
            tier: License tier
            email: Customer email
            metadata: Additional metadata
            
        Returns:
            tuple: (success, message, client_secret)
        """
        try:
            import stripe
            
            amount = int(self.get_tier_price(tier) * 100)  # Convert to cents
            
            if amount == 0:
                return False, "Free tier does not require payment", None
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                receipt_email=email,
                metadata=metadata or {},
                description=f"MultiTeam {tier.title()} License"
            )
            
            info("PaymentSystem", f"Payment intent created: {intent.id}")
            return True, "Payment intent created", intent.client_secret
            
        except Exception as e:
            error("PaymentSystem", f"Error creating payment intent: {e}")
            return False, str(e), None
    
    def create_subscription_stripe(self, tier: str, email: str, payment_method_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create Stripe subscription
        
        Args:
            tier: License tier
            email: Customer email
            payment_method_id: Stripe payment method ID
            
        Returns:
            tuple: (success, message, subscription_id)
        """
        try:
            import stripe
            
            # Create customer
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"MultiTeam {tier.title()} License"
                        },
                        "unit_amount": int(self.get_tier_price(tier) * 100),
                        "recurring": {
                            "interval": "month"
                        }
                    }
                }],
                expand=["latest_invoice.payment_intent"]
            )
            
            info("PaymentSystem", f"Subscription created: {subscription.id}")
            return True, "Subscription created successfully", subscription.id
            
        except Exception as e:
            error("PaymentSystem", f"Error creating subscription: {e}")
            return False, str(e), None
    
    def verify_payment_stripe(self, payment_intent_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Verify Stripe payment
        
        Args:
            payment_intent_id: Payment intent ID
            
        Returns:
            tuple: (success, message, payment_data)
        """
        try:
            import stripe
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                payment_data = {
                    "transaction_id": intent.id,
                    "amount": intent.amount / 100,
                    "currency": intent.currency,
                    "email": intent.receipt_email,
                    "status": "paid"
                }
                
                info("PaymentSystem", f"Payment verified: {payment_intent_id}")
                return True, "Payment successful", payment_data
            else:
                return False, f"Payment status: {intent.status}", None
                
        except Exception as e:
            error("PaymentSystem", f"Error verifying payment: {e}")
            return False, str(e), None
    
    def create_payment_paypal(self, tier: str, return_url: str, cancel_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create PayPal payment
        
        Args:
            tier: License tier
            return_url: Return URL after payment
            cancel_url: Cancel URL
            
        Returns:
            tuple: (success, message, approval_url)
        """
        try:
            import paypalrestsdk
            
            amount = self.get_tier_price(tier)
            
            if amount == 0:
                return False, "Free tier does not require payment", None
            
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"MultiTeam {tier.title()} License",
                            "sku": tier,
                            "price": f"{amount:.2f}",
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": f"{amount:.2f}",
                        "currency": "USD"
                    },
                    "description": f"MultiTeam {tier.title()} License - Monthly Subscription"
                }]
            })
            
            if payment.create():
                # Get approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        info("PaymentSystem", f"PayPal payment created: {payment.id}")
                        return True, "Payment created", link.href
                
                return False, "No approval URL found", None
            else:
                error("PaymentSystem", f"PayPal payment error: {payment.error}")
                return False, str(payment.error), None
                
        except Exception as e:
            error("PaymentSystem", f"Error creating PayPal payment: {e}")
            return False, str(e), None
    
    def execute_payment_paypal(self, payment_id: str, payer_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Execute PayPal payment
        
        Args:
            payment_id: Payment ID
            payer_id: Payer ID
            
        Returns:
            tuple: (success, message, payment_data)
        """
        try:
            import paypalrestsdk
            
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                payment_data = {
                    "transaction_id": payment.id,
                    "amount": float(payment.transactions[0].amount.total),
                    "currency": payment.transactions[0].amount.currency,
                    "status": "paid"
                }
                
                info("PaymentSystem", f"PayPal payment executed: {payment_id}")
                return True, "Payment successful", payment_data
            else:
                error("PaymentSystem", f"PayPal execution error: {payment.error}")
                return False, str(payment.error), None
                
        except Exception as e:
            error("PaymentSystem", f"Error executing PayPal payment: {e}")
            return False, str(e), None
    
    def cancel_subscription_stripe(self, subscription_id: str) -> Tuple[bool, str]:
        """
        Cancel Stripe subscription
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            tuple: (success, message)
        """
        try:
            import stripe
            
            subscription = stripe.Subscription.delete(subscription_id)
            
            info("PaymentSystem", f"Subscription cancelled: {subscription_id}")
            return True, "Subscription cancelled successfully"
            
        except Exception as e:
            error("PaymentSystem", f"Error cancelling subscription: {e}")
            return False, str(e)
    
    def handle_webhook_stripe(self, payload: str, sig_header: str, webhook_secret: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Handle Stripe webhook
        
        Args:
            payload: Webhook payload
            sig_header: Signature header
            webhook_secret: Webhook secret
            
        Returns:
            tuple: (success, event_type, event_data)
        """
        try:
            import stripe
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            event_type = event['type']
            event_data = event['data']['object']
            
            info("PaymentSystem", f"Webhook received: {event_type}")
            return True, event_type, event_data
            
        except Exception as e:
            error("PaymentSystem", f"Webhook error: {e}")
            return False, str(e), None


# Debug logging
debug("PaymentSystem", "Payment system module loaded")

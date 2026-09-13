"""
SURE SAVINGS: Synthetic Transaction Generator & Multi-Profile Seed Data
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

def get_canonical_user_profile() -> Dict[str, Any]:
    return {
        "user_id": "usr_arjun_01",
        "name": "Arjun K.",
        "initials": "AK",
        "occupation": "Gig Platform Worker",
        "title": "Delivery & Freelance Lead",
        "platforms": ["Zomato", "Blinkit", "Fiverr"],
        "currency": "INR",
        "current_week": "Week 36",
        "current_income": 8400.0,
        "stabilized_income": 7100.0,
        "forecast_next_week": 6900.0,
        "forecast_confidence": 0.92,
        "income_volatility": 0.31,
        "current_buffer": 6800.0,
        "buffer_target": 15000.0,
        "protected_floor": 3500.0,
        "weekly_burn": 4400.0,
        "current_coverage_weeks": 1.5,
        "safe_to_use_above_floor": 3300.0,
        "surplus": 1300.0,
        "recommended_contribution": 900.0,
        "free_pocket_liquidity": 400.0,
        "resilience_score": 74,
        "risk_score": 23
    }

def get_canonical_weekly_history() -> List[Dict[str, Any]]:
    """
    12-Week Rolling History for Arjun K. (W25 to W36) + W37 projected
    """
    return [
        {"week": "W25", "income": 7100, "stabilized": 7100, "status": "Normal"},
        {"week": "W26", "income": 6800, "stabilized": 7100, "status": "Normal"},
        {"week": "W27", "income": 7400, "stabilized": 7100, "status": "Normal"},
        {"week": "W28", "income": 5100, "stabilized": 7100, "status": "Monsoon Drop (Low)"},
        {"week": "W29", "income": 6700, "stabilized": 7100, "status": "Normal"},
        {"week": "W30", "income": 7200, "stabilized": 7100, "status": "Normal"},
        {"week": "W31", "income": 9600, "stabilized": 7100, "status": "Festival Peak (High)"},
        {"week": "W32", "income": 6900, "stabilized": 7100, "status": "Normal"},
        {"week": "W33", "income": 7300, "stabilized": 7100, "status": "Normal"},
        {"week": "W34", "income": 6850, "stabilized": 7100, "status": "Normal"},
        {"week": "W35", "income": 7100, "stabilized": 7100, "status": "Normal"},
        {"week": "W36", "income": 8400, "stabilized": 7100, "status": "Surplus (+18%)", "current": True},
        {"week": "W37 (Exp)", "income": 6900, "stabilized": 7100, "status": "Forecast Corridor", "forecast": True}
    ]

def get_canonical_current_inflows() -> List[Dict[str, Any]]:
    return [
        {
            "id": "tx_inf_01",
            "date": "Sep 03, 2026",
            "source": "Zomato Delivery Payout",
            "platform": "Zomato Deliveries",
            "category": "Gig Platform",
            "type": "credit",
            "amount": 4900.0,
            "status": "Verified / Settled"
        },
        {
            "id": "tx_inf_02",
            "date": "Sep 03, 2026",
            "source": "Blinkit Quick Fleet Payout",
            "platform": "Blinkit Quick Fleet",
            "category": "Gig Platform",
            "type": "credit",
            "amount": 2600.0,
            "status": "Verified / Settled"
        },
        {
            "id": "tx_inf_03",
            "date": "Sep 03, 2026",
            "source": "Direct Freelance UI Design",
            "platform": "Contract Client",
            "category": "Direct Freelance",
            "type": "credit",
            "amount": 900.0,
            "status": "Verified / Settled"
        }
    ]

def get_canonical_scheduled_outflows() -> List[Dict[str, Any]]:
    return [
        {
            "id": "obl_01",
            "date": "Sep 06, 2026",
            "time": "08:00 AM",
            "description": "Residential Shared Room Rent",
            "category": "Housing",
            "type": "debit",
            "amount": 2800.0,
            "essential": True,
            "impact": "Safe (+₹5,600 above floor)"
        },
        {
            "id": "obl_02",
            "date": "Sep 08, 2026",
            "time": "11:00 AM",
            "description": "Shell Fast Battery Swap",
            "category": "Work Transit",
            "type": "debit",
            "amount": 1200.0,
            "essential": True,
            "impact": "Safe (+₹4,400 above floor)"
        },
        {
            "id": "obl_03",
            "date": "Sep 10, 2026",
            "time": "09:00 AM",
            "description": "HDFC EV Two-Wheeler EMI",
            "category": "Mobility Asset",
            "type": "debit",
            "amount": 4500.0,
            "essential": True,
            "impact": "Attention Needed (+₹620 above floor)",
            "timing_risk": True,
            "timing_note": "Debits at 09:00 AM; batch payout settles at 06:00 PM."
        },
        {
            "id": "obl_04",
            "date": "Sep 10, 2026",
            "time": "06:00 PM",
            "description": "Zomato Weekly Fleet Settlement",
            "category": "Gig Inflow",
            "type": "credit",
            "amount": 6900.0,
            "essential": False,
            "impact": "High Confidence (92%)"
        },
        {
            "id": "obl_05",
            "date": "Sep 15, 2026",
            "time": "10:00 AM",
            "description": "BESCOM Power & Fiber Utility",
            "category": "Utilities",
            "type": "debit",
            "amount": 1800.0,
            "essential": True,
            "impact": "Safe (+₹5,720 above floor)"
        }
    ]

def get_canonical_activity_log() -> List[Dict[str, Any]]:
    return [
        {
            "id": "act_01",
            "time": "Today, 09:30 AM",
            "title": "Recommendation Generated: Safe-to-Save ₹900",
            "detail": "Calculated from ₹1,300 surplus over ₹7,100 baseline. Preserves ₹400 free pocket cash while keeping essential ₹3,500 floor untouched.",
            "type": "recommendation"
        },
        {
            "id": "act_02",
            "time": "Today, 09:15 AM",
            "title": "Payout Reconciliation Complete",
            "detail": "3 platform deposits verified via aggregator: Zomato (₹4,900), Blinkit (₹2,600), Direct UI (₹900). Total cycle earnings confirmed: ₹8,400.",
            "type": "inflow"
        },
        {
            "id": "act_03",
            "time": "Today, 08:45 AM",
            "title": "Volatility Matrix Recalibrated",
            "detail": "12-week stabilized baseline updated to ₹7,100 via formula 0.60*Median + 0.40*Average.",
            "type": "engine"
        },
        {
            "id": "act_04",
            "time": "Sep 01, 2026",
            "title": "Resilience Score Recalculated: +6 pts",
            "detail": "Score elevated from 68 to 74/100 due to improved runway stability (1.5 weeks of fixed expenditure covered).",
            "type": "resilience"
        },
        {
            "id": "act_05",
            "time": "Aug 28, 2026",
            "title": "Monsoon Downpour Inflow Anomaly Detected",
            "detail": "Temporary dip to ₹5,100 successfully absorbed by buffer reserve without triggering emergency loans or payment failures.",
            "type": "anomaly"
        }
    ]

def get_canonical_ledger_history() -> List[Dict[str, Any]]:
    """Comprehensive 25-transaction ledger across the past 30 days"""
    return [
        {"id": "tx_01", "date": "Sep 03, 2026", "source": "Zomato Delivery Weekly Settlement", "platform": "Zomato Fleet", "category": "Gig Platform", "direction": "credit", "amount": 4900.0, "status": "Settled", "essential": False},
        {"id": "tx_02", "date": "Sep 03, 2026", "source": "Blinkit Quick Commerce Payout", "platform": "Blinkit Fleet", "category": "Gig Platform", "direction": "credit", "amount": 2600.0, "status": "Settled", "essential": False},
        {"id": "tx_03", "date": "Sep 03, 2026", "source": "Direct Freelance Poster UI Design", "platform": "Contract Client", "category": "Direct Freelance", "direction": "credit", "amount": 900.0, "status": "Settled", "essential": False},
        {"id": "tx_04", "date": "Sep 02, 2026", "source": "Shell Fast Battery Swap Station", "platform": "Shell Recharge", "category": "Transit", "direction": "debit", "amount": 350.0, "status": "Settled", "essential": True},
        {"id": "tx_05", "date": "Sep 02, 2026", "source": "BPCL Two-Wheeler Fuel", "platform": "BPCL Outlet", "category": "Transit", "direction": "debit", "amount": 420.0, "status": "Settled", "essential": True},
        {"id": "tx_06", "date": "Sep 01, 2026", "source": "Jio Fiber & Mobile Plan Recharge", "platform": "Jio Payments", "category": "Utilities", "direction": "debit", "amount": 699.0, "status": "Settled", "essential": True},
        {"id": "tx_07", "date": "Sep 01, 2026", "source": "D-Mart Supermarket Essentials", "platform": "D-Mart", "category": "Essential Living", "direction": "debit", "amount": 1450.0, "status": "Settled", "essential": True},
        {"id": "tx_08", "date": "Aug 31, 2026", "source": "Apollo Pharmacy Emergency Medicine", "platform": "Apollo", "category": "Health", "direction": "debit", "amount": 320.0, "status": "Settled", "essential": True},
        {"id": "tx_09", "date": "Aug 30, 2026", "source": "EV Bike Brake Pad Service", "platform": "Mechanic Workshop", "category": "Mobility Asset", "direction": "debit", "amount": 650.0, "status": "Settled", "essential": True},
        {"id": "tx_10", "date": "Aug 29, 2026", "source": "Swiggy Rain Surge Incentive", "platform": "Swiggy Partner", "category": "Gig Platform", "direction": "credit", "amount": 1200.0, "status": "Settled", "essential": False},
        {"id": "tx_11", "date": "Aug 29, 2026", "source": "Mid-Shift Refreshment & Chai", "platform": "UPI Merchant", "category": "Discretionary", "direction": "debit", "amount": 85.0, "status": "Settled", "essential": False},
        {"id": "tx_12", "date": "Aug 28, 2026", "source": "HDFC ATM Cash Withdrawal", "platform": "HDFC Bank", "category": "Cash", "direction": "debit", "amount": 2000.0, "status": "Settled", "essential": True},
        {"id": "tx_13", "date": "Aug 27, 2026", "source": "Helmet Waterproof Mobile Mount", "platform": "Amazon Pay", "category": "Equipment", "direction": "debit", "amount": 890.0, "status": "Settled", "essential": True},
        {"id": "tx_14", "date": "Aug 27, 2026", "source": "Zomato Customer In-App Tips", "platform": "Zomato Fleet", "category": "Gig Platform", "direction": "credit", "amount": 450.0, "status": "Settled", "essential": False},
        {"id": "tx_15", "date": "Aug 26, 2026", "source": "Ather Grid Fast Charging", "platform": "Ather Energy", "category": "Transit", "direction": "debit", "amount": 240.0, "status": "Settled", "essential": True},
        {"id": "tx_16", "date": "Aug 25, 2026", "source": "Residential Shared Room Rent", "platform": "Direct Owner UPI", "category": "Housing", "direction": "debit", "amount": 2800.0, "status": "Settled", "essential": True},
        {"id": "tx_17", "date": "Aug 24, 2026", "source": "BESCOM Electricity Utility", "platform": "BESCOM", "category": "Utilities", "direction": "debit", "amount": 1150.0, "status": "Settled", "essential": True},
        {"id": "tx_18", "date": "Aug 23, 2026", "source": "Blinkit On-Time Delivery Bonus", "platform": "Blinkit Fleet", "category": "Gig Platform", "direction": "credit", "amount": 800.0, "status": "Settled", "essential": False},
        {"id": "tx_19", "date": "Aug 22, 2026", "source": "Battery Swapping Station Fee", "platform": "Yulu Fleet", "category": "Transit", "direction": "debit", "amount": 350.0, "status": "Settled", "essential": True},
        {"id": "tx_20", "date": "Aug 21, 2026", "source": "Local Kirana Store Groceries", "platform": "UPI Merchant", "category": "Essential Living", "direction": "debit", "amount": 180.0, "status": "Settled", "essential": True},
        {"id": "tx_21", "date": "Aug 20, 2026", "source": "Raincoat & Phone Screen Guard", "platform": "Local Accessories", "category": "Equipment", "direction": "debit", "amount": 250.0, "status": "Settled", "essential": False},
        {"id": "tx_22", "date": "Aug 19, 2026", "source": "Rapido Captain Weekend Trips", "platform": "Rapido Captain", "category": "Gig Platform", "direction": "credit", "amount": 1650.0, "status": "Settled", "essential": False},
        {"id": "tx_23", "date": "Aug 18, 2026", "source": "Airtel Emergency Data Pack", "platform": "Airtel Thanks", "category": "Utilities", "direction": "debit", "amount": 149.0, "status": "Settled", "essential": True},
        {"id": "tx_24", "date": "Aug 17, 2026", "source": "EV Battery Swap Pass Renewal", "platform": "Shell Recharge", "category": "Transit", "direction": "debit", "amount": 350.0, "status": "Settled", "essential": True},
        {"id": "tx_25", "date": "Aug 15, 2026", "source": "Previous Buffer Automated Allocation", "platform": "Smart Buffer Vault", "category": "Buffer", "direction": "credit", "amount": 900.0, "status": "Settled", "essential": False}
    ]


"""
SURE SAVINGS 8.0: Goal Allocation & Optimization Service
Dynamically allocates available Safe-to-Save capacity across competing goals
based on urgency, goal priority, financial risk, and floor preservation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class GoalAllocationService:
    """
    Optimizes safe-to-save allocation across competing financial goals.
    Emergency reserve and fixed rent commitments take priority during high risk;
    longer-term growth and vehicle assets gain allocation as resilience improves.
    """

    @classmethod
    def optimize_allocation(
        cls,
        digital_twin: Dict[str, Any],
        goals: Optional[List[Dict[str, Any]]] = None,
        monthly_savings_pool: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Extracts telemetry from digital_twin and distributes monthly safe-to-save pool.
        """
        p = digital_twin.get("observation", {}).get("profile", {}) or digital_twin.get("profile", {}) or digital_twin
        dec = digital_twin.get("decisions", {})
        
        safe_to_save_rec = float(p.get("recommended_contribution", dec.get("safe_to_save", {}).get("recommended_save", 0.0)))
        pool = float(monthly_savings_pool) if monthly_savings_pool is not None else (safe_to_save_rec * 4.0)
        
        goals_list = goals or digital_twin.get("observation", {}).get("goals", [])
        
        risk = int(p.get("risk_score", 23))
        resilience = int(p.get("resilience_score", 74))
        floor = float(p.get("protected_floor", 3500.0))
        curr_buf = float(p.get("current_buffer", 0.0))
        target_buf = float(p.get("buffer_target", 15000.0))
        gap = max(0.0, target_buf - curr_buf)
        
        res = cls.allocate(
            available_safe_to_save=pool,
            goals=goals_list,
            risk_score=risk,
            resilience_score=resilience,
            protected_floor=floor,
            buffer_gap=gap
        )
        res["status"] = "OPTIMIZED"
        return res

    @classmethod
    def allocate(
        cls,
        available_safe_to_save: float,
        goals: List[Dict[str, Any]],
        risk_score: int = 25,
        resilience_score: int = 74,
        protected_floor: float = 3500.0,
        buffer_gap: float = 8200.0
    ) -> Dict[str, Any]:
        """
        Distributes safe-to-save capacity across user goals.
        """
        if available_safe_to_save <= 0 or not goals:
            return {
                "available_capacity": available_safe_to_save,
                "total_allocated": 0.0,
                "unallocated_pocket": max(0.0, available_safe_to_save),
                "allocations": [],
                "strategy_note": "No active goals or zero safe-to-save capacity available."
            }

        # Normalize goals
        active_goals = []
        for g in goals:
            is_active = g.get("is_active", True)
            if not is_active:
                continue
            curr = float(g.get("current_amount", g.get("current", 0.0)))
            tgt = float(g.get("target_amount", g.get("target", 0.0)))
            gap = max(0.0, tgt - curr)
            if gap <= 0 and tgt > 0:
                continue # Already funded
            
            prio = str(g.get("priority", "medium")).lower()
            g_type = str(g.get("goal_type", "GENERAL")).upper()
            
            # Numeric priority weight: 1=highest, 4=lowest
            if "emerg" in g_type or "reserve" in g_type or prio == "high" or "priority 1" in prio:
                prio_rank = 1
            elif "rent" in g_type or "emi" in g_type or prio == "medium" or "priority 2" in prio:
                prio_rank = 2
            elif "vehicle" in g_type or "repair" in g_type or "priority 3" in prio:
                prio_rank = 3
            else:
                prio_rank = 4

            active_goals.append({
                "id": g.get("id"),
                "name": g.get("name", "Goal"),
                "goal_type": g_type,
                "target_amount": tgt,
                "current_amount": curr,
                "remaining_gap": gap,
                "priority_rank": prio_rank,
                "priority_label": f"Priority {prio_rank}"
            })

        if not active_goals:
            return {
                "available_capacity": available_safe_to_save,
                "total_allocated": 0.0,
                "unallocated_pocket": available_safe_to_save,
                "allocations": [],
                "strategy_note": "All active goals are 100% funded!"
            }

        # Sort goals by priority rank (1 = emergency reserve, 2 = rent, 3 = vehicle, etc.)
        sorted_goals = sorted(active_goals, key=lambda x: x["priority_rank"])

        # Risk-sensitive distribution weights
        # When risk is high (>50): 75% Priority 1, 20% Priority 2, 5% Priority 3
        # When risk is moderate (25-50): 60% Priority 1, 25% Priority 2, 15% Priority 3
        # When risk is low (<25): 45% Priority 1, 30% Priority 2, 25% Priority 3
        if risk_score > 50:
            weights = {1: 0.75, 2: 0.20, 3: 0.05, 4: 0.0}
            strategy_note = "High financial risk: Emergency reserve and rent safety take 95% priority."
        elif risk_score >= 30:
            weights = {1: 0.60, 2: 0.25, 3: 0.15, 4: 0.0}
            strategy_note = "Moderate risk: Prioritizing emergency buffer runway before secondary assets."
        else:
            weights = {1: 0.45, 2: 0.30, 3: 0.20, 4: 0.05}
            strategy_note = "Strong resilience: Balanced allocation accelerating secondary and long-term goals."

        allocations = []
        remaining_capacity = available_safe_to_save

        for g in sorted_goals:
            rank = g["priority_rank"]
            w = weights.get(rank, 0.10)
            
            # Target share
            nominal_alloc = round((available_safe_to_save * w) / 50.0) * 50.0
            
            # Bound by remaining capacity and goal gap
            actual_alloc = min(nominal_alloc, remaining_capacity, g["remaining_gap"])
            remaining_capacity = max(0.0, remaining_capacity - actual_alloc)

            allocations.append({
                "goal_id": g["id"],
                "goal_name": g["name"],
                "priority_label": g["priority_label"],
                "priority_rank": g["priority_rank"],
                "allocated_amount": actual_alloc,
                "remaining_gap_after": max(0.0, g["remaining_gap"] - actual_alloc),
                "progress_percentage": round(((g["current_amount"] + actual_alloc) / max(1.0, g["target_amount"])) * 100, 1),
                "est_weeks_to_completion": max(1, int(round((g["remaining_gap"] - actual_alloc) / max(50.0, actual_alloc)))) if (g["remaining_gap"] - actual_alloc) > 0 else 0
            })

        # If any capacity remains (e.g. earlier goals capped out), allocate to first unfilled goal
        if remaining_capacity > 0:
            for a in allocations:
                if a["remaining_gap_after"] > 0:
                    add_amt = min(remaining_capacity, a["remaining_gap_after"])
                    a["allocated_amount"] += add_amt
                    a["remaining_gap_after"] -= add_amt
                    remaining_capacity -= add_amt
                    if remaining_capacity <= 0:
                        break

        total_allocated = sum(a["allocated_amount"] for a in allocations)

        return {
            "available_capacity": available_safe_to_save,
            "total_allocated": total_allocated,
            "unallocated_pocket": max(0.0, available_safe_to_save - total_allocated),
            "strategy_note": strategy_note,
            "risk_score_used": risk_score,
            "allocations": allocations,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }

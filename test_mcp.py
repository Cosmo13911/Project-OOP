import asyncio
import random
from system import GreenValleySystem
from models.enum import Tier, TournamentStatus, BookingStatus

async def run_comprehensive_test():
    # --- [1] System Initialization ---
    system = GreenValleySystem()
    system.create_data()
    print("--- Phase 1: System Initialized ---")

    # --- [2] Member Discovery ---
    jennie = system.find_user("M-001")
    course_c1 = system.find_course("C-001")
    print(f"User: {jennie.name} | Tier: {jennie.tier.name} | Phone: {jennie.phone}")

    # --- [3] Resource Reuse Test (Today & Tomorrow) ---
    print("\n--- Phase 2: Resource Reuse Test ---")
    date_today = "12-03-2026"
    date_tomorrow = "13-03-2026"
    time_slot = "09:00"

    # Day 1 Booking
    booking_day1 = system.create_booking("M-001", "C-001", date_today, time_slot)
    available_caddies = system.find_available_caddies(date_today, time_slot)
    selected_caddy = available_caddies[0]
    
    booking_day1.assign_caddy(selected_caddy)
    selected_caddy.assign_to_schedule(booking_day1)
    print(f"Day 1 ({date_today}): Assigned Caddy '{selected_caddy.name}'")

    # Day 2 Booking (Same Caddy)
    try:
        booking_day2 = system.create_booking("M-001", "C-001", date_tomorrow, time_slot)
        if selected_caddy.is_available(date_tomorrow, time_slot):
            booking_day2.assign_caddy(selected_caddy)
            selected_caddy.assign_to_schedule(booking_day2)
            print(f"Day 2 ({date_tomorrow}): Successfully reused Caddy '{selected_caddy.name}' [PASSED]")
        else:
            print(f"Day 2 ({date_tomorrow}): Caddy '{selected_caddy.name}' not available [FAILED]")
    except Exception as e:
        print(f"Error in Day 2 booking: {e}")

    # --- [4] Ordering & Stock Test ---
    print("\n--- Phase 3: Ordering & Stock Management ---")
    product = system.find_product("P-001")
    initial_stock = product.stock
    order_qty = 2
    
    order_result = system.place_order(booking_day1.booking_id, "P-001", order_qty)
    print(f"Order Result: {order_result} | Stock: {initial_stock} -> {product.stock}")

    # --- [5] Rain Check & Receipt Validation ---
    print("\n--- Phase 4: Rain Check & Receipt Validation ---")
    rc_value = 500.0
    rain_check = system.issue_raincheck_to_user("M-001", rc_value)
    print(f"Rain Check Issued: {rain_check.code} for amount {rain_check.amount}")

    # Process Payment for Day 1
    payment_result = system.process_payment(booking=booking_day1, rain_check_code=rain_check.code)
    print(f"Payment Status: {payment_result['status']}")

    # Verify Receipt Details
    payment = system.payments[-1]
    receipt = payment.get_transaction_details()
    
    print("--- Detailed Receipt ---")
    print(f"Base Price: {receipt['base_price']} THB")
    print(f"Member Discount: -{receipt['discount']} THB")
    print(f"Add-ons (Caddy/Food): +{receipt['addons_price']} THB")
    print(f"Rain Check applied: -{receipt['rain_check_coupon']} THB")
    print(f"Total Net: {receipt['total_net']} THB")

    # Math Verification
    expected = (receipt['base_price'] - receipt['discount']) + receipt['addons_price'] - receipt['rain_check_coupon']
    if abs(expected - receipt['total_net']) < 0.01:
        print("Calculation Check: [SUCCESS]")
    else:
        print(f"Calculation Check: [FAILED] Expected {expected}")

    # --- [6] Full Tournament Lifecycle ---
    print("\n--- Phase 5: Tournament Lifecycle & Handicap ---")
    tour_data = system.create_tournament("Global Golf Open", "15-04-2026", 1500.0, "C-001")
    tour_id = tour_data["tournamentID"]

    # Register players (M-001 to M-004)
    for i in range(1, 5):
        system.process_registration_payment(f"M-00{i}", tour_id)
    
    # Close registration and pair players
    system.close_registration_and_pairing(tour_id)
    
    # Simulate scoring 18 holes
    for i in range(1, 5):
        for hole in range(1, 19):
            system.record_tournament_score(tour_id, f"M-00{i}", hole, random.randint(3, 6))
    
    # End tournament and check Handicap
    prev_hc = jennie.current_handicap
    system.end_tournament(tour_id)
    print(f"Tournament Ended. Jennie's Handicap: {prev_hc} -> {jennie.current_handicap}")
    print(f"History Records: {len(jennie.history)}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
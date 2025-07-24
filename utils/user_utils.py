def format_user_list(active_users, left_users):
    active_section = "\n🟢 Active Users:\n" + "\n".join(f"  • {user}" for user in active_users) if active_users else "\n🟢 No active users"
    left_section = "\n🔴 Disconnected Users:\n" + "\n".join(f"  • {user}" for user in left_users) if left_users else ""
    return active_section + "\n" + left_section

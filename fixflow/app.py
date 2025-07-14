import streamlit as st
import json
import os
import bcrypt
from datetime import datetime
import base64
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

USER_DATA_FILE = 'users.json'
TASKS_FILE = 'tasks.json'
CONFIG_FILE = 'config.json'

# Inject custom CSS for overall UI (remove red bar and navbar styles)
st.markdown("""
    <style>
    body, .stApp {
        background-color: #e6f2ff !important;
    }
    .stButton>button {
        background-color: #1976d2;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        margin: 0.5rem 0;
        border: none;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #1565c0;
        color: #fff;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div>input {
        background-color: #f0f7ff;
        border-radius: 6px;
    }
    .stTextArea>div>textarea {
        background-color: #f0f7ff;
        border-radius: 6px;
    }
    .stHeader, .stSubheader {
        color: #1976d2;
        font-weight: bold;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1976d2;
        font-weight: bold;
    }
    .login-role-bar {
        background: #FFF9ED;
        color: #222;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.3rem 1rem;
        border-radius: 8px;
        margin-bottom: 1.2rem;
        text-align: center;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
    }
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #1976d2 0%, #ffe066 100%);
        border-radius: 20px;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .welcome-title {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .welcome-subtitle {
        color: #f0f0f0;
        font-size: 1.5rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    .get-started-btn {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        padding: 1rem 3rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .get-started-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .logout-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background-color: #1976d2;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .logout-btn:hover {
        background-color: #1565c0;
    }
    </style>
""", unsafe_allow_html=True)

# Remove sidebar role selection and top bar

# Handle manual "rerun" workaround for older Streamlit versions
if 'reload' in st.session_state:
    del st.session_state['reload']

# Initialize welcome page state
if 'show_welcome' not in st.session_state:
    st.session_state['show_welcome'] = True

def create_default_users_file():
    if not os.path.exists(USER_DATA_FILE):
        default_super_admin_password = "superadmin123"
        hashed = bcrypt.hashpw(default_super_admin_password.encode(), bcrypt.gensalt()).decode()
        users_data = {
            "super_admin": {
                "superadmin": hashed
            },
            "admin": {},
            "users": {}
        }
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users_data, f, indent=4)
        st.info("Created default users.json with superadmin/superadmin123")

def create_default_tasks_file():
    if not os.path.exists(TASKS_FILE):
        tasks_data = {
            "tasks": {}
        }
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks_data, f, indent=4)

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        create_default_users_file()
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        create_default_tasks_file()
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(data):
    with open(TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "projects": ["VK-IU","VK-I","VK-W","LE","CubesAt"],
            "departments": ["Avionics"],
            "assignors": [],
            "categorization_1": ["IS-1/2U"],
            "categorization_2": ["Soldering"],
            "technicians": [],
            "cost_center": ["Launch"]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login(username, password, role):
    users = load_users()
    if username in users.get(role, {}):
        stored_hash = users[role][username]
        if verify_password(password, stored_hash):
            return True
    return False

def logout():
    # Get the current role before clearing session state
    current_role = st.session_state.get('role', '')
    current_username = st.session_state.get('username', '')
    
    # Clear session state
    for key in ['is_logged_in', 'username', 'role', 'admin_logged_in_success', 'super_admin_logged_in_success']:
        st.session_state.pop(key, None)
    
    # Display success message based on role
    if current_role == "super_admin":
        st.success(f"Super Admin '{current_username}' has successfully logged out!")
    elif current_role == "admin":
        st.success(f"Admin '{current_username}' has successfully logged out!")
    elif current_role == "users":
        st.success(f"Technician '{current_username}' has successfully logged out!")
    else:
        st.success("You have successfully logged out!")
    
    # Reset welcome page state
    st.session_state['show_welcome'] = True
    st.session_state['reload'] = True
    st.query_params = {"reload": "true"}
    st.stop()

def register_user(new_username, new_password, role):
    users = load_users()
    if new_username in users.get(role, {}):
        return False, f"{role.title()} already exists."
    users[role][new_username] = hash_password(new_password)
    save_users(users)
    return True, f"{role.title()} registered successfully!"

def create_task(assigned_to, task_description, assigned_by):
    tasks = load_tasks()
    task_id = f"task_{len(tasks['tasks']) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    tasks['tasks'][task_id] = {
        "assigned_to": assigned_to,
        "task_description": task_description,
        "assigned_by": assigned_by,
        "assigned_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "pending",
        "completion_image": None,
        "completion_date": None,
        "completion_notes": None
    }
    save_tasks(tasks)
    return True, f"Task assigned to {assigned_to} successfully!"

def update_task(task_id, completion_image, completion_notes):
    tasks = load_tasks()
    if task_id in tasks['tasks']:
        tasks['tasks'][task_id]['status'] = 'completed'
        tasks['tasks'][task_id]['completion_image'] = completion_image
        tasks['tasks'][task_id]['completion_notes'] = completion_notes
        tasks['tasks'][task_id]['completion_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_tasks(tasks)
        return True, "Task updated successfully!"
    return False, "Task not found!"

def get_user_tasks(username):
    tasks = load_tasks()
    user_tasks = {}
    for task_id, task in tasks['tasks'].items():
        if task['assigned_to'] == username:
            user_tasks[task_id] = task
    return user_tasks

def get_all_tasks():
    tasks = load_tasks()
    return tasks['tasks']

# Initialize session state variables
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'super_admin_logged_in_success' not in st.session_state:
    st.session_state['super_admin_logged_in_success'] = False
if 'admin_logged_in_success' not in st.session_state:
    st.session_state['admin_logged_in_success'] = False

create_default_users_file()
create_default_tasks_file()

# Welcome page
if st.session_state.get('show_welcome', True) and not st.session_state.get('is_logged_in', False):
    st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">🚀Fixflow Technician Task Manager </div>
            <div class="welcome-subtitle">Streamlining Operations. Empowering Technicians.</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Get Started", key="get_started_btn", use_container_width=True):
            st.session_state['show_welcome'] = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
            <p>Your Command Center for Field Technicians</p>
        </div>
    """, unsafe_allow_html=True)

# Show login page only after "Get Started" is clicked
elif not st.session_state.get('is_logged_in', False):
    menu = st.sidebar.selectbox("Choose Login Type", ["Super Admin Login", "Admin Login", "User Login"])
    st.markdown(f'<div class="login-role-bar">{menu}</div>', unsafe_allow_html=True)

    if menu == "Super Admin Login":
        if not st.session_state['super_admin_logged_in_success']:
            st.subheader("Super Admin Login")
            super_admin_user = st.text_input("Super Admin Username")
            super_admin_pass = st.text_input("Super Admin Password", type='password')
            if st.button("Login as Super Admin"):
                if login(super_admin_user, super_admin_pass, "super_admin"):
                    st.session_state['is_logged_in'] = True
                    st.session_state['username'] = super_admin_user
                    st.session_state['role'] = "super_admin"
                    st.session_state['super_admin_logged_in_success'] = True
                    st.success("Super Admin logged in!")
                    st.session_state['reload'] = True
                    st.query_params = {"reload": "true"}
                    st.stop()
                else:
                    st.error("Invalid super admin credentials")
        else:
            st.success("You are logged in successfully as Super Admin.")
            st.markdown("---")
            st.subheader("Add Admin Users")
            new_admin = st.text_input("New Admin Username")
            new_admin_pass = st.text_input("New Admin Password", type='password')
            if st.button("Add Admin"):
                if not new_admin or not new_admin_pass:
                    st.error("Please enter both username and password.")
                else:
                    success, msg = register_user(new_admin, new_admin_pass, "admin")
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

            st.markdown("---")
            st.subheader("Add Technician Users")
            new_tech = st.text_input("New Technician Username", key="super_tech_user")
            new_tech_pass = st.text_input("New Technician Password", type='password', key="super_tech_pass")
            if st.button("Add Technician", key="super_tech_button"):
                if not new_tech or not new_tech_pass:
                    st.error("Please enter both username and password.")
                else:
                    success, msg = register_user(new_tech, new_tech_pass, "users")
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

            if st.button("Logout", key="super_logout"):
                logout()

    elif menu == "Admin Login":
        if not st.session_state['admin_logged_in_success']:
            st.subheader("Admin Login")
            admin_user = st.text_input("Admin Username")
            admin_pass = st.text_input("Admin Password", type='password')
            if st.button("Login as Admin"):
                if login(admin_user, admin_pass, "admin"):
                    st.session_state['is_logged_in'] = True
                    st.session_state['username'] = admin_user
                    st.session_state['role'] = "admin"
                    st.session_state['admin_logged_in_success'] = True
                    st.success("Admin logged in!")
                    st.session_state['reload'] = True
                    st.query_params = {"reload": "true"}
                    st.stop()
                else:
                    st.error("Invalid admin credentials")
        else:
            st.success("You are logged in successfully as Admin.")
            st.markdown("---")
            st.subheader("Add Technician Users")
            new_user = st.text_input("New Technician Username")
            new_pass = st.text_input("New Technician Password", type='password')
            if st.button("Add Technician"):
                if not new_user or not new_pass:
                    st.error("Please enter both username and password.")
                else:
                    success, msg = register_user(new_user, new_pass, "users")
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

            if st.button("Logout"):
                logout()

    elif menu == "User Login":
        st.subheader("User Login")
        user = st.text_input("Username")
        user_pass = st.text_input("Password", type='password')
        if st.button("Login as User"):
            if login(user, user_pass, "users"):
                st.session_state['is_logged_in'] = True
                st.session_state['username'] = user
                st.session_state['role'] = "users"
                st.success(f"Welcome, {user}!")
                st.session_state['reload'] = True
                st.query_params = {"reload": "true"}
                st.stop()
            else:
                st.error("Invalid user credentials")

else:
    # Logged in state
    st.sidebar.write(f"👤 Logged in as: `{st.session_state['username']}`")
    
    # Add logout button in top right corner only
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Logout", key="top_logout_btn", help="Click to logout"):
            logout()
    
    if st.session_state['role'] == "super_admin":
        selected_page = st.sidebar.selectbox("Navigate", ["Dashboard", "Manage Users", "View All Tasks", "Field Configuration"])
    elif st.session_state['role'] == "admin":
        selected_page = st.sidebar.selectbox("Navigate", ["Dashboard", "Assign Tasks", "View Tasks"])
    else:  # users/technicians
        selected_page = st.sidebar.selectbox("Navigate", ["Dashboard", "My Tasks"])

    # Technician Dashboard
    if selected_page == "Dashboard" and st.session_state['role'] == "users":
        st.header("🧑‍🔧 Technician Dashboard")
        st.success(f"You are successfully logged in as Technician: {st.session_state['username']}")
        # Efficiency points calculation
        user_tasks = get_user_tasks(st.session_state['username'])
        total_tasks = len(user_tasks)
        completed_tasks = sum(1 for t in user_tasks.values() if t['status'] == 'completed')
        efficiency_points = completed_tasks * 10  # Example: 10 points per completed task
        st.metric("Efficiency Points", efficiency_points)
        st.metric("Total Tasks Assigned", total_tasks)
        st.metric("Tasks Completed", completed_tasks)
        st.markdown("---")
        st.subheader("Your Assigned Tasks")
        if not user_tasks:
            st.info("No tasks assigned to you yet.")
        else:
            for task_id, task in user_tasks.items():
                with st.expander(f"Task {task_id}"):
                    st.write(f"**Task Description:** {task['task_description']}")
                    st.write(f"**Assigned By:** {task['assigned_by']}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Assigned Date:** {task.get('assigned_date', 'N/A')}")
                    if 'deadline' in task:
                        st.write(f"**Deadline:** {task['deadline']}")
                    if task['status'] == 'completed':
                        st.write(f"**Completed On:** {task.get('completion_date', 'N/A')}")
                        if task.get('completion_notes'):
                            st.write(f"**Completion Notes:** {task['completion_notes']}")
                        if task.get('completion_image'):
                            st.write("**Completion Image:**")
                            st.image(base64.b64decode(task['completion_image']), caption="Task Completion Image")
                        st.success("Task has been completed. You have earned 10 points!")
                    else:
                        # Pending task: allow completion
                        with st.form(f"complete_form_{task_id}"):
                            completion_notes = st.text_area("Completion Notes", key=f"notes_{task_id}")
                            completion_image = st.file_uploader("Upload Proof Image", type=["jpg", "jpeg", "png"], key=f"img_{task_id}")
                            submitted = st.form_submit_button("Mark as Completed")
                            if submitted:
                                if not completion_notes.strip():
                                    st.error("Please enter completion notes.")
                                elif not completion_image:
                                    st.error("Please upload a proof image.")
                                else:
                                    # Read and encode image
                                    img_bytes = completion_image.read()
                                    img_b64 = base64.b64encode(img_bytes).decode()
                                    success, msg = update_task(task_id, img_b64, completion_notes)
                                    if success:
                                        st.success("Task has been completed. You have earned 10 points!")
                                        st.rerun()
                                    else:
                                        st.error(msg)
        st.markdown("---")

    # Technician My Tasks Page
    if selected_page == "My Tasks" and st.session_state['role'] == "users":
        st.header("📝 My Tasks")
        user_tasks = get_user_tasks(st.session_state['username'])
        st.subheader("Your Assigned Tasks")
        if not user_tasks:
            st.info("No tasks assigned to you yet.")
        else:
            for task_id, task in user_tasks.items():
                with st.expander(f"Task {task_id}"):
                    st.write(f"**Task Description:** {task['task_description']}")
                    st.write(f"**Assigned By:** {task['assigned_by']}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Assigned Date:** {task.get('assigned_date', 'N/A')}")
                    if 'deadline' in task:
                        st.write(f"**Deadline:** {task['deadline']}")
                    if task['status'] == 'completed':
                        st.write(f"**Completed On:** {task.get('completion_date', 'N/A')}")
                        if task.get('completion_notes'):
                            st.write(f"**Completion Notes:** {task['completion_notes']}")
                        if task.get('completion_image'):
                            st.write("**Completion Image:**")
                            st.image(base64.b64decode(task['completion_image']), caption="Task Completion Image")
                        st.success("Task has been completed. You have earned 10 points!")
                    else:
                        # Pending task: allow completion
                        with st.form(f"complete_form_my_{task_id}"):
                            completion_notes = st.text_area("Completion Notes", key=f"notes_my_{task_id}")
                            completion_image = st.file_uploader("Upload Proof Image", type=["jpg", "jpeg", "png"], key=f"img_my_{task_id}")
                            submitted = st.form_submit_button("Mark as Completed")
                            if submitted:
                                if not completion_notes.strip():
                                    st.error("Please enter completion notes.")
                                elif not completion_image:
                                    st.error("Please upload a proof image.")
                                else:
                                    img_bytes = completion_image.read()
                                    img_b64 = base64.b64encode(img_bytes).decode()
                                    success, msg = update_task(task_id, img_b64, completion_notes)
                                    if success:
                                        st.success("Task has been completed. You have earned 10 points!")
                                        st.rerun()
                                    else:
                                        st.error(msg)
        st.markdown("---")

    if selected_page == "Manage Users" and st.session_state['role'] == "super_admin":
        st.header("👥 Manage Users")
        
        # Add Admin
        st.subheader("➕ Add Admin")
        new_admin = st.text_input("New Admin Username", key="manage_admin_user")
        new_admin_pass = st.text_input("New Admin Password", type='password', key="manage_admin_pass")
        if st.button("Add Admin", key="manage_admin_button"):
            if not new_admin or not new_admin_pass:
                st.error("Please enter both username and password.")
            else:
                success, msg = register_user(new_admin, new_admin_pass, "admin")
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown("---")
        
        # Remove Admin
        st.subheader("🗑️ Remove Admin")
        users = load_users()
        admins = users.get('admin', {})
        if admins:
            admin_to_remove = st.selectbox("Select Admin to Remove", list(admins.keys()), key="remove_admin_manage")
            if st.button("Remove Admin", key="remove_admin_btn_manage"):
                users['admin'].pop(admin_to_remove, None)
                save_users(users)
                st.success(f"Admin '{admin_to_remove}' removed successfully.")
                st.rerun()
        else:
            st.info("No admins to remove.")
        st.markdown("---")

        # Add Technician
        st.subheader("➕ Add Technician")
        new_tech = st.text_input("New Technician Username", key="manage_tech_user")
        new_tech_pass = st.text_input("New Technician Password", type='password', key="manage_tech_pass")
        if st.button("Add Technician", key="manage_tech_button"):
            if not new_tech or not new_tech_pass:
                st.error("Please enter both username and password.")
            else:
                success, msg = register_user(new_tech, new_tech_pass, "users")
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown("---")
        
        # Remove Technician
        st.subheader("🗑️ Remove Technician")
        technicians = users.get('users', {})
        if technicians:
            tech_to_remove = st.selectbox("Select Technician to Remove", list(technicians.keys()), key="remove_tech_manage")
            if st.button("Remove Technician", key="remove_tech_btn_manage"):
                users['users'].pop(tech_to_remove, None)
                save_users(users)
                st.success(f"Technician '{tech_to_remove}' removed successfully.")
                st.rerun()
        else:
            st.info("No technicians to remove.")
        st.markdown("---")

    if selected_page == "View All Tasks" and st.session_state['role'] == "super_admin":
        st.header("📋 All Tasks Overview")
        tasks = get_all_tasks()
        
        if not tasks:
            st.info("No tasks have been created yet.")
        else:
            for task_id, task in tasks.items():
                with st.expander(f"Task {task_id} - {task['assigned_to']}"):
                    if 'project' in task:
                        st.write(f"**Project:** {task['project']}")
                    st.write(f"**Assigned to:** {task['assigned_to']}")
                    st.write(f"**Task:** {task['task_description']}")
                    st.write(f"**Assigned by:** {task['assigned_by']}")
                    st.write(f"**Status:** {task['status']}")
                    assigned_date = task.get('assigned_date') or task.get('assigned_time', 'N/A')
                    st.write(f"**Assigned Date:** {assigned_date}")
                    if task['status'] == 'completed':
                        st.write(f"**Completed:** {task['completion_date']}")
                        if task['completion_notes']:
                            st.write(f"**Notes:** {task['completion_notes']}")

    # Super Admin Dashboard
    if selected_page == "Dashboard" and st.session_state['role'] == "super_admin":
        st.header("👑 Super Admin Dashboard")
        st.success(f"You are logged in successfully as Super Admin: {st.session_state['username']}")
        users = load_users()
        tasks = get_all_tasks()
        st.subheader("📊 User Analytics")
        super_admins = users.get('super_admin', {})
        admins = users.get('admin', {})
        technicians = users.get('users', {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Super Admins", len(super_admins))
        with col2:
            st.metric("Admins", len(admins))
        with col3:
            st.metric("Technicians", len(technicians))
        with col4:
            st.metric("Total Users", len(super_admins) + len(admins) + len(technicians))
        st.markdown("---")
        # Admins statistics
        st.subheader("🛡️ Admins - Pending Tasks")
        admin_stats = []
        for admin in admins:
            pending = sum(1 for t in tasks.values() if t.get('assigned_by') == admin and t['status'] == 'pending')
            total = sum(1 for t in tasks.values() if t.get('assigned_by') == admin)
            admin_stats.append({"Admin": admin, "Total Tasks Assigned": total, "Pending Tasks": pending})
        if admin_stats:
            st.dataframe(admin_stats, use_container_width=True)
        else:
            st.info("No admins or no tasks assigned by admins yet.")
        st.markdown("---")
        # Technicians statistics
        st.subheader("🧑‍🔧 Technicians - Pending Tasks")
        tech_stats = []
        for tech in technicians:
            pending = sum(1 for t in tasks.values() if t.get('assigned_to') == tech and t['status'] == 'pending')
            total = sum(1 for t in tasks.values() if t.get('assigned_to') == tech)
            tech_stats.append({"Technician": tech, "Total Tasks Assigned": total, "Pending Tasks": pending})
        if tech_stats:
            st.dataframe(tech_stats, use_container_width=True)
        else:
            st.info("No technicians or no tasks assigned to technicians yet.")
        st.markdown("---")

    # Super Admin Field Configuration Page
    if selected_page == "Field Configuration" and st.session_state['role'] == "super_admin":
        st.header("🛠 Field Configuration")
        config = load_config()
        st.info("Super Admins can manage these fields. Changes affect the Assign Tasks form.")
        def manage_list(label, key, help_text=None):
            st.subheader(label)
            items = config[key]
            new_item = st.text_input(f"Add new {label}", key=f"add_{key}_superadmin", help=help_text)
            if st.button(f"Add {label}", key=f"btn_add_{key}_superadmin"):
                if new_item and new_item not in items:
                    items.append(new_item)
                    config[key] = items
                    save_config(config)
                    st.success(f"Added {new_item} to {label}")
                    st.rerun()
            if items:
                remove_item = st.selectbox(f"Remove {label}", ["-"] + items, key=f"remove_{key}_superadmin")
                if remove_item != "-" and st.button(f"Remove {label}", key=f"btn_remove_{key}_superadmin"):
                    items.remove(remove_item)
                    config[key] = items
                    save_config(config)
                    st.success(f"Removed {remove_item} from {label}")
                    st.rerun()
            st.markdown("---")
        manage_list("Project", "projects", help_text="E.g., VK-IU")
        manage_list("Department", "departments", help_text="E.g., Avionics")
        manage_list("Assignor", "assignors", help_text="E.g., Supervisor/Engineer names")
        manage_list("Categorization - 1", "categorization_1", help_text="E.g., IS-1/2U")
        manage_list("Categorization - 2", "categorization_2", help_text="E.g., Soldering")
        manage_list("Technician", "technicians", help_text="Technician names for task assignment")
        manage_list("Cost Center", "cost_center", help_text="E.g., Launch, Ground, Flight")
        st.markdown("---")

    if selected_page == "Dashboard" and st.session_state['role'] == "admin":
        st.header("🛠 Admin Dashboard")
        st.success("You are logged in successfully as Admin.")

        # Display task statistics
        tasks = get_all_tasks()
        pending_tasks = sum(1 for task in tasks.values() if task['status'] == 'pending')
        completed_tasks = sum(1 for task in tasks.values() if task['status'] == 'completed')

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pending Tasks", pending_tasks)
        with col2:
            st.metric("Completed Tasks", completed_tasks)

        # Load users and tasks
        users = load_users()
        technicians = list(users.get("users", {}).keys())

        # Prepare data
        data = []
        for tech in technicians:
            total = 0
            completed = 0
            pending = 0
            last_completed_date = None
            for task in tasks.values():
                if task["assigned_to"] == tech:
                    total += 1
                    if task["status"] == "completed":
                        completed += 1
                        last_completed_date = task.get("completion_date", last_completed_date)
                    else:
                        pending += 1
            data.append({
                "Technician": tech,
                "Total Tasks": total,
                "Completed Tasks": completed,
                "Pending Tasks": pending,
                "Last Completed": last_completed_date
            })

        df = pd.DataFrame(data)

        # --- Available Technicians ---
        st.subheader("🟢 Available Technicians")
        available_techs = [row["Technician"] for row in data if row["Pending Tasks"] == 0]
        if available_techs:
            st.success(f"Available for assignment: {', '.join(available_techs)}")
        else:
            st.info("No technicians are currently fully available (all have pending tasks).")

        # --- AI Recommendation for Task Assignment ---
        st.subheader("🤖 AI Recommendation for Task Assignment")
        if data:
            sorted_techs = sorted(data, key=lambda x: (x["Pending Tasks"], x["Total Tasks"], x["Last Completed"] if x["Last Completed"] else ""))
            recommended = sorted_techs[0]["Technician"]
            st.info(f"Recommended Technician: **{recommended}** (Least pending workload)")
        else:
            st.info("No technician data available for recommendation.")

        # --- Technician Task Overview (Dropdown Chart Selection) ---
        st.subheader("📊 Technician Task Overview")
        chart_options = [
            "Bar Chart",
            "Stacked Bar Chart",
            "Donut Chart",
            "Pie Chart",
            "Altair Bar Chart",
            "Progress Bars",
            "Data Table",
            "Summary Statistics"
        ]
        selected_chart = st.selectbox("Select Chart Type", chart_options, key="admin_chart_type")
        if not df.empty:
            if selected_chart == "Bar Chart":
                fig_bar = px.bar(
                    df,
                    x="Technician",
                    y="Total Tasks",
                    title="Total Tasks by Technician",
                    color="Total Tasks",
                    color_continuous_scale="viridis",
                    template="plotly_white"
                )
                fig_bar.update_layout(title_font_size=16, title_font_color="#1976d2", showlegend=False, height=350)
                st.plotly_chart(fig_bar, use_container_width=True)
            elif selected_chart == "Stacked Bar Chart":
                fig_stacked = px.bar(
                    df,
                    x="Technician",
                    y=["Completed Tasks", "Pending Tasks"],
                    title="Task Status by Technician",
                    barmode="stack",
                    color_discrete_map={"Completed Tasks": "#4CAF50", "Pending Tasks": "#FF9800"},
                    template="plotly_white"
                )
                fig_stacked.update_layout(title_font_size=16, title_font_color="#1976d2", height=350)
                st.plotly_chart(fig_stacked, use_container_width=True)
            elif selected_chart == "Donut Chart":
                total_completed = df["Completed Tasks"].sum()
                total_pending = df["Pending Tasks"].sum()
                fig_donut = go.Figure(data=[go.Pie(
                    labels=["Completed", "Pending"],
                    values=[total_completed, total_pending],
                    hole=0.6,
                    marker_colors=["#4CAF50", "#FF9800"]
                )])
                fig_donut.update_layout(title="Overall Task Status Distribution", title_font_size=16, title_font_color="#1976d2", height=350)
                st.plotly_chart(fig_donut, use_container_width=True)
            elif selected_chart == "Pie Chart":
                selected_tech = st.selectbox("Select Technician for Pie Chart", df["Technician"].tolist(), key="admin_pie_tech")
                tech_data = df[df["Technician"] == selected_tech].iloc[0]
                fig_pie = px.pie(
                    values=[tech_data["Completed Tasks"], tech_data["Pending Tasks"]],
                    names=["Completed", "Pending"],
                    title=f"Task Status for {selected_tech}",
                    color_discrete_map={"Completed": "#4CAF50", "Pending": "#FF9800"}
                )
                fig_pie.update_layout(title_font_size=16, title_font_color="#1976d2", height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            elif selected_chart == "Altair Bar Chart":
                df_melt = df.melt(id_vars=["Technician"], value_vars=["Completed Tasks", "Pending Tasks"], var_name="Task Status", value_name="Count")
                chart = alt.Chart(df_melt).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                    x=alt.X("Technician:N", title="Technician", sort="-y"),
                    y=alt.Y("Count:Q", title="Number of Tasks"),
                    color=alt.Color("Task Status:N", scale=alt.Scale(range=["#4CAF50", "#FF9800"])),
                    tooltip=["Technician", "Task Status", "Count"]
                ).properties(title="Task Distribution by Technician", width=600, height=350).configure_title(fontSize=16, color="#1976d2")
                st.altair_chart(chart, use_container_width=True)
            elif selected_chart == "Progress Bars":
                for _, row in df.iterrows():
                    total = row["Total Tasks"]
                    completed = row["Completed Tasks"]
                    pending = row["Pending Tasks"]
                    if total > 0:
                        completion_rate = (completed / total) * 100
                        col1, col2, col3 = st.columns([2, 3, 1])
                        with col1:
                            st.write(f"**{row['Technician']}**")
                        with col2:
                            st.progress(float(completion_rate / 100))
                        with col3:
                            st.write(f"{completion_rate:.1f}%")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", int(total))
                        with col2:
                            st.metric("Completed", int(completed), delta=f"+{int(completed)}")
                        with col3:
                            st.metric("Pending", int(pending), delta=f"-{int(pending)}")
                        st.markdown("---")
            elif selected_chart == "Data Table":
                df_display = df.copy()
                df_display["Completion Rate (%)"] = df_display.apply(
                    lambda row: round((row["Completed Tasks"] / row["Total Tasks"]) * 100, 1) if row["Total Tasks"] > 0 else 0, axis=1
                )
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    column_config={
                        "Technician": st.column_config.TextColumn("Technician", width="medium"),
                        "Total Tasks": st.column_config.NumberColumn("Total Tasks", format="%d"),
                        "Completed Tasks": st.column_config.NumberColumn("Completed Tasks", format="%d"),
                        "Pending Tasks": st.column_config.NumberColumn("Pending Tasks", format="%d"),
                        "Completion Rate (%)": st.column_config.NumberColumn("Completion Rate (%)", format="%.1f%%")
                    }
                )
            elif selected_chart == "Summary Statistics":
                st.markdown("---")
                st.subheader("📈 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Technicians", len(df))
                with col2:
                    st.metric("Total Tasks", df["Total Tasks"].sum())
                with col3:
                    st.metric("Completed Tasks", df["Completed Tasks"].sum())
                with col4:
                    avg_completion = (df["Completed Tasks"].sum() / df["Total Tasks"].sum() * 100) if df["Total Tasks"].sum() > 0 else 0
                    st.metric("Avg Completion Rate", f"{avg_completion:.1f}%")
        else:
            st.info("No technician data available for dashboard.")

    if selected_page == "Assign Tasks" and st.session_state['role'] == "admin":
        st.header("📝 Assign Tasks")
        config = load_config()
        users = load_users()
        all_technicians = list(users.get("users", {}).keys())

        # Find available technicians (no pending tasks)
        tasks = get_all_tasks()
        available_techs = []
        for tech in all_technicians:
            pending = sum(1 for t in tasks.values() if t["assigned_to"] == tech and t["status"] == "pending")
            if pending == 0:
                available_techs.append(tech)

        # Cost Center dropdown (mandatory, default to 'Launch')
        cost_center_options = config.get("cost_center", ["Launch"])
        default_cost_center_index = 0
        if "Launch" in cost_center_options:
            default_cost_center_index = cost_center_options.index("Launch")
        cost_center = st.selectbox("Cost Center", cost_center_options, index=default_cost_center_index)

        project = st.selectbox("Project", config["projects"])
        department = st.selectbox("Department", config["departments"])
        assignor = st.selectbox("Assignor", [st.session_state["username"]])
        categorization_1 = st.selectbox("Categorization - 1", config["categorization_1"])
        categorization_2 = st.selectbox("Categorization - 2", config["categorization_2"])
        identification_no = st.text_input("Identification No (Design Doc/Task Ref)")

        # Recommend available technician
        recommended_tech = available_techs[0] if available_techs else (all_technicians[0] if all_technicians else "")
        st.info(f"Recommended Technician: {recommended_tech if recommended_tech else 'No available technician'}")

        assigned_to = st.selectbox("Assignee (Technician)", available_techs if available_techs else all_technicians, index=0 if recommended_tech in (available_techs if available_techs else all_technicians) else 0)
        assigned_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task_description = st.text_area("Task Description", height=100)
        is_urgent = st.checkbox("Mark as Urgent", value=False)
        deadline = st.date_input("Deadline to Complete Task")
        deadline_str = deadline.strftime('%Y-%m-%d') if deadline else ""

        if st.button("Assign Task"):
            required_fields = [cost_center, project, department, assignor, assigned_to]
            if not all(required_fields):
                st.error("Cost Center, Project, Department, Assignor, and Assignee are required.")
            elif not task_description.strip():
                st.error("Please enter a task description.")
            elif not deadline_str:
                st.error("Please select a deadline.")
            else:
                # Save all fields in the task
                tasks = load_tasks()
                task_id = f"task_{len(tasks['tasks']) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                tasks['tasks'][task_id] = {
                    "cost_center": cost_center,
                    "project": project,
                    "department": department,
                    "assignor": assignor,
                    "categorization_1": categorization_1,
                    "categorization_2": categorization_2,
                    "identification_no": identification_no,
                    "assigned_to": assigned_to,
                    "assigned_date": assigned_time,
                    "task_description": task_description,
                    "assigned_by": st.session_state['username'],
                    "status": "pending",
                    "urgent": is_urgent,
                    "deadline": deadline_str,
                    "completion_image": None,
                    "completion_date": None,
                    "completion_notes": None
                }
                save_tasks(tasks)
                st.success(f"Task assigned to {assigned_to} successfully!{' (Urgent)' if is_urgent else ''} Deadline: {deadline_str}")

    if selected_page == "View Tasks" and st.session_state['role'] == "admin":
        st.header("📋 View All Tasks")
        tasks = get_all_tasks()
        
        if not tasks:
            st.info("No tasks have been created yet.")
        else:
            for task_id, task in tasks.items():
                with st.expander(f"Task {task_id} - {task['assigned_to']}"):
                    if 'cost_center' in task:
                        st.write(f"**Cost Center:** {task['cost_center']}")
                    if 'project' in task:
                        st.write(f"**Project:** {task['project']}")
                    st.write(f"**Assigned to:** {task['assigned_to']}")
                    st.write(f"**Task:** {task['task_description']}")
                    st.write(f"**Assigned by:** {task['assigned_by']}")
                    st.write(f"**Status:** {task['status']}")
                    assigned_date = task.get('assigned_date') or task.get('assigned_time', 'N/A')
                    st.write(f"**Assigned Date:** {assigned_date}")
                    if 'deadline' in task:
                        st.write(f"**Deadline:** {task['deadline']}")
                    if task['status'] == 'completed':
                        st.write(f"**Completed:** {task['completion_date']}")
                        if task['completion_notes']:
                            st.write(f"**Notes:** {task['completion_notes']}")
                        if task['completion_image']:
                            st.write("**Completion Image:**")
                            st.image(base64.b64decode(task['completion_image']), caption="Task Completion Image")

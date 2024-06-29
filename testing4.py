import streamlit as st
import json
from datetime import datetime, timedelta
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

class UserVisitTracker:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data = self.load_user_data()
        self.today = datetime.now().date()

        self.update_visit_log()
        self.save_user_data()

    def load_user_data(self):
        try:
            with open(f"{self.user_id}_data.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "last_visit": None,
                "consecutive_days": 0,
                "total_days": 0,
                "visit_dates": {},
                "daily_time_spent": {}
            }

    def save_user_data(self):
        with open(f"{self.user_id}_data.json", "w") as f:
            json.dump(self.user_data, f)

    def update_visit_log(self):
        last_visit = self.user_data.get("last_visit")
        if last_visit:
            last_visit = datetime.strptime(last_visit, "%Y-%m-%d").date()

        if last_visit is None or self.today != last_visit:
            self.user_data["total_days"] += 1
            self.user_data["visit_dates"][str(self.today)] = True

            if last_visit is None or (self.today - last_visit).days > 1:
                self.user_data["consecutive_days"] = 1
            else:
                self.user_data["consecutive_days"] += 1

            self.user_data["last_visit"] = str(self.today)

            time_spent = random.randint(1, 120)
            self.user_data["daily_time_spent"][str(self.today)] = time_spent

    def display_user_info(self):
        st.write(f"User ID: {self.user_id}")
        st.write(f"Last visit: {self.user_data.get('last_visit')}")
        st.write(f"Total days visited: {self.user_data['total_days']}")
        st.button(f"⭐ {self.user_data['consecutive_days']}")
        return self.user_data['consecutive_days']

    def generate_calendar(self, dates):
        start_date = min(dates)
        end_date = max(dates)
        date_range = pd.date_range(start=start_date, end=end_date)
        calendar_data = {
            "day": [],
            "month": [],
            "visited": []
        }
        for date in date_range:
            calendar_data["day"].append(date.day)
            calendar_data["month"].append(date.strftime('%B'))
            calendar_data["visited"].append(date in dates)
        return calendar_data

    def display_visit_calendar(self):
        st.write("### Visit Calendar")
        visit_dates = [datetime.strptime(date, "%Y-%m-%d") for date in self.user_data["visit_dates"]]

        calendar_data = self.generate_calendar(visit_dates)
        calendar_df = pd.DataFrame(calendar_data)

        fig = go.Figure()

        for month in calendar_df['month'].unique():
            month_df = calendar_df[calendar_df['month'] == month]
            fig.add_trace(go.Scatter(
                x=month_df['day'],
                y=[month] * len(month_df),
                mode='markers',
                marker=dict(
                    size=12,
                    color=['#1f77b4' if visited else '#FFFFFF' for visited in month_df['visited']],
                    line=dict(color='black', width=1)
                ),
                text=month_df['day'],
                name=month
            ))

        fig.update_layout(
            title="Visit Calendar",
            yaxis=dict(title='Month', tickmode='array', tickvals=[i for i in range(len(calendar_df['month'].unique()))], ticktext=calendar_df['month'].unique()),
            xaxis=dict(title='Day', tickmode='array', tickvals=list(range(1, 32)), ticktext=list(range(1, 32))),
            showlegend=False,
            height=600,
        )

        st.plotly_chart(fig)

    def display_time_spent(self):
        st.write("### Time Spent per Day (in hours)")

        time_spent_df = pd.DataFrame(list(self.user_data["daily_time_spent"].items()), columns=["Date", "Time Spent (minutes)"])
        time_spent_df["Date"] = pd.to_datetime(time_spent_df["Date"])
        time_spent_df["Day of Week"] = time_spent_df["Date"].dt.day_name()
        time_spent_df["Time Spent (hours)"] = time_spent_df["Time Spent (minutes)"] / 60

        time_spent_per_day = time_spent_df.groupby("Day of Week").agg({
            "Time Spent (hours)": "sum"
        }).reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ).reset_index()

        fig_time_spent = px.bar(
            time_spent_per_day,
            x="Day of Week",
            y="Time Spent (hours)",
            title="Time Spent per Day (in hours)",
            labels={"Time Spent (hours)": "Time Spent (hours)"}
        )

        fig_time_spent.update_layout(
            xaxis_title="Day of the Week",
            yaxis_title="Time Spent (hours)",
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig_time_spent)


# def main():
#     user_id = 'user123'
#     tracker = UserVisitTracker(user_id)
#     tracker.display_user_info()
#     tracker.display_visit_calendar()
#     tracker.display_time_spent()

# if __name__ == "__main__":
#     main()

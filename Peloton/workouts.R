library(conflicted)  
library(tidyverse)
library(dplyr)
conflict_prefer("filter", "dplyr")
conflict_prefer("lag", "dplyr")

#workouts <- read.csv("~/Downloads/Rlynch3456_workouts-4-2-2024.csv")
workouts <- read.csv("~/Documents/Fitness/Rlynch3456_workouts_2024.csv")

name_freq <- table(workouts$Instructor.Name)
name_freq_df <- as.data.frame(name_freq)
name_freq_df <- name_freq_df[order(-name_freq_df$Freq), ]                    

ggplot(name_freq_df, aes(x = reorder(Var1, Freq), y = Freq)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  coord_flip() +  # Horizontal bars
  labs(x = "Instructor", y = "Count", title = "Count of Instructor") +
  theme_minimal()

disc_freq <- table(workouts$Fitness.Discipline)
disc_freq_df <- as.data.frame(disc_freq) 
disc_freq_df <- disc_freq_df[order(-disc_freq_df$Freq), ]

ggplot(disc_freq_df, aes(x = reorder(Var1, Freq), y = Freq)) + 
  geom_bar(stat = "identity", fill = "skyblue") + 
  coord_flip() + # Horizontal bars 
  labs(x = "Fitness Discipline", y = "Count", title = "Count of Discipline") + 
  theme_minimal() 

rides <- filter(workouts, Fitness.Discipline == "Cycling")

df <- rides %>% 
  mutate(date_column = as.Date(rides$Workout, format="%m/%d/%y"))
 
ride_summary_data <- df %>% 
  mutate(month = format(date_column, "%Y-%m")) %>% 
  group_by(month) %>% 
  summarise(monthly_distance = sum(Distance..mi.))


ggplot(ride_summary_data, aes(x=month, y=monthly_distance)) +
  geom_point() +
  theme( axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1)) +
  xlab("Month") + ylab("Total Cycling Distance (miles)")

df <- workouts %>% 
  mutate(date_column = as.Date(workouts$Workout, format="%m/%d/%y"))

time_summary_data <- df %>% 
  mutate(month = format(date_column, "%Y-%m")) %>% 
  group_by(month) %>% 
  summarise(monthly_time = sum(Length..minutes.))


ggplot(time_summary_data, aes(x=month, y=monthly_time/60)) +
  geom_point(size=3, color="blue", alpha=0.5) +
  theme( axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1)) +
  xlab("Month") + ylab("Total Workouts Time (hours)")

#filtered_data <- df %>% 
#  filter(month >= '2023-01-01')  

workouts$date <- as.Date(workouts$Workout, format = "%m/%d/%y")
workouts$month <-format(workouts$date, "%Y-%m")
filtered_data <- workouts %>% 
  filter(date >= as.Date("2024-01-01"))

# Group by month and discipline, and calculate total duration for each group
monthly_totals <- workouts %>%
  group_by(month, Fitness.Discipline) %>%
  summarise(total_duration = sum(Length..minutes.), average_duration = mean(Length..minutes.), .groups='keep') 

# Print or view the monthly totals
print(monthly_totals)

monthly_totals %>% 
  ggplot(aes(month, total_duration/60, color=Fitness.Discipline))+
  geom_point(size=5, alpha=0.5) +
  labs(title="Total Workout Time", x="Year-Month", y="Time (Hours)")+
  theme_bw() + 
  theme(axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1))

monthly_totals %>% 
  ggplot(aes(month, average_duration/60, color=Fitness.Discipline))+
  geom_point(size=5, alpha=0.5) +
  labs(title="Average Workout Time", x="Year-Month", y="Time (Hours)")+
  theme_bw() + 
  theme(axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1))

monthly_totals %>% 
  ggplot(aes(month, y=total_duration/60, fill=Fitness.Discipline))+
  geom_bar(position="stack", stat="identity") +
  labs(title="Total Workout Time", x="Year-Month", y="Time (Hours)")+
  theme_bw() + 
  theme(axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1))

# Let's look at average speed over time
monthly_rides <- workouts %>% 
  filter(Fitness.Discipline == "Cycling") %>% 
  filter(Length..minutes. > 10)  %>% 
  filter(Avg..Speed..mph. > 0)

# Group by month and discipline, and calculate average speed and watts for each group
monthly_rides <- monthly_rides%>%
  group_by(month) %>%
  summarise(average_speed = mean(Avg..Speed..mph.), average_power = mean(Avg..Watts), .groups='keep')

print(monthly_rides)
monthly_rides %>% 
  ggplot(aes(month, average_speed))+
  geom_point(size=5, alpha=0.5, color="blue") +
  labs(title="Average Speed Over Time", x="Year-Month", y="Avg. Speed (MPH)")+
  theme_bw() + 
  theme(axis.text.x = element_text(angle=90, vjust = 0.5, hjust = 1))



View(rides)

rides %>% 
  filter(Distance..mi. > 0) %>% 
  filter(Length..minutes. > 10) %>% 
ggplot(aes(Length..minutes., Avg..Speed..mph.)) +
  labs(title="Speed versus Ride Length", x="Ride Length (Minutes)", y="Speed (MPH)")+
  scale_x_continuous(breaks = scales::pretty_breaks(n = 10)) +
  scale_y_continuous(breaks = scales::pretty_breaks(n = 10))+
  geom_point(size=5, alpha=0.5, color="blue")



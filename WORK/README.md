# Онтология темы «Как ставить цели»

## Диаграмма концептов

```mermaid
graph TD
  classDef core fill:#f9f,stroke:#333;
  classDef aux fill:#bbf,stroke:#333;

  GoalSetting[Постановка целей] --> Goal[Цель]
  GoalSetting --> Motivation[Мотивация]
  GoalSetting --> ActionPlan[План действий]

  Goal --> SMART[SMART критерии]
  Goal --> Deadline[Срок]
  Goal --> Reward[Награда]

  Motivation --> Reward
  ActionPlan --> Deadline
  SMART --> Deadline

  class Goal,Motivation,ActionPlan core
  class SMART,Deadline,Reward aux

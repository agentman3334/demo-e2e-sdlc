export const TASK_STATUSES = {
  todo: { label: 'To Do', color: 'default' },
  in_progress: { label: 'In Progress', color: 'processing' },
  in_review: { label: 'In Review', color: 'warning' },
  done: { label: 'Done', color: 'success' },
};

export const PRIORITY_COLORS = {
  low: 'blue',
  medium: 'orange',
  high: 'red',
  critical: 'magenta',
};

export const PROJECT_STATUSES = {
  active: { label: 'Active', color: 'green' },
  on_hold: { label: 'On Hold', color: 'orange' },
  completed: { label: 'Completed', color: 'blue' },
  archived: { label: 'Archived', color: 'default' },
};
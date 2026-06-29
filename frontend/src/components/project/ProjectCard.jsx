import { Card, Tag, Typography, Progress } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PROJECT_STATUSES } from '../../utils/constants';
import dayjs from 'dayjs';

export default function ProjectCard({ project, progress = 0 }) {
  const navigate = useNavigate();
  const statusInfo = PROJECT_STATUSES[project.status] || PROJECT_STATUSES.active;

  return (
    <Card
      hoverable
      onClick={() => navigate(`/projects/${project.id}`)}
      style={{ marginBottom: 16 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Typography.Title level={5} style={{ margin: 0 }}>{project.name}</Typography.Title>
        <Tag color={statusInfo.color}>{statusInfo.label}</Tag>
      </div>
      {project.description && (
        <Typography.Paragraph type="secondary" ellipsis={{ rows: 2 }} style={{ marginTop: 8 }}>
          {project.description}
        </Typography.Paragraph>
      )}
      <Progress percent={progress} size="small" style={{ marginTop: 8 }} />
      {project.deadline && (
        <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
          <CalendarOutlined /> {dayjs(project.deadline).format('MMM D, YYYY')}
        </div>
      )}
    </Card>
  );
}
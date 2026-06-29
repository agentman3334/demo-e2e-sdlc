import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Progress, Spin } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ProjectOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import analyticsApi from '../api/analyticsApi';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    analyticsApi.getDashboard()
      .then(({ data }) => setStats(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Typography.Title level={3} style={{ marginBottom: 24 }}>Dashboard</Typography.Title>
      <Row gutter={16} style={{ marginBottom: 32 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Tasks"
              value={stats?.total_tasks || 0}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Completed"
              value={stats?.completed || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={stats?.in_progress || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Overdue"
              value={stats?.overdue || 0}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>
      <Typography.Title level={4} style={{ marginBottom: 16 }}>Project Progress</Typography.Title>
      <Row gutter={[16, 16]}>
        {(stats?.projects || []).map((project) => (
          <Col xs={24} sm={12} lg={8} key={project.id}>
            <Card hoverable onClick={() => navigate(`/projects/${project.id}`)}>
              <Typography.Text strong>{project.name}</Typography.Text>
              <Progress percent={project.progress} style={{ marginTop: 8 }} />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
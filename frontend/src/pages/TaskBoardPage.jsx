import { useParams } from 'react-router-dom';
import TaskBoard from '../components/task/TaskBoard';

export default function TaskBoardPage() {
  const { id } = useParams();
  return <TaskBoard projectId={id} />;
}

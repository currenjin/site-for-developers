import { Link } from 'react-router-dom';

const NotFound = () => {
    return (
        <div className="p-2 rounded-2xl border-2 border-indigo-600">
                <span className="text-3xl">404 Not Found</span>
                <br/>
                <Link to="/">홈으로 돌아가기</Link>
        </div>
    );
};

export default NotFound;

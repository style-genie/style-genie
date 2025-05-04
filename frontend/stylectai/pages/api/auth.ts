import { setCookie } from 'cookies-next';
import type { NextApiRequest, NextApiResponse } from 'next';

type Data = {
  sessionId: string;
};

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  if (req.method === 'POST') {
    const { username, bearerToken } = req.body;

    // TODO: Authenticate user with username and bearerToken

    // Generate a session ID based on the username
    const sessionId = username + '-' + Math.random().toString(36).substring(2, 15);

    // Set the session ID in a cookie
    setCookie('sessionId', sessionId, { req, res, maxAge: 60 * 60 * 24 });

    // Return the session ID
    res.status(200).json({ sessionId: sessionId });
  } else {
    // Handle any other HTTP method
    res.status(405).end();
  }
}

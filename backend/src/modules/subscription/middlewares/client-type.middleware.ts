import { Request, Response, NextFunction } from 'express';

import { Injectable, Logger, NestMiddleware } from '@nestjs/common';

import { REQUEST_TEMPLATE_TYPE_VALUES } from '@remnawave/backend-contract';

@Injectable()
export class ClientTypeMiddleware implements NestMiddleware {
    private readonly logger = new Logger(ClientTypeMiddleware.name);
    private readonly allowedClientTypes: ReadonlySet<string> = new Set(
        REQUEST_TEMPLATE_TYPE_VALUES,
    );

    use(req: Request, res: Response, next: NextFunction) {
        const clientTypeParam = req.params.clientType;
        const clientType = Array.isArray(clientTypeParam) ? clientTypeParam[0] : clientTypeParam;

        if (clientType && !this.allowedClientTypes.has(clientType)) {
            this.logger.error(`Invalid client type: ${clientType}`);

            res.socket?.destroy();
            return;
        }

        next();
    }
}

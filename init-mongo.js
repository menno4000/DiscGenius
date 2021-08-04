db.createUser(
    {
        user: "dg_admin",
        pwd: "12345",
        roles: [{
            role: 'readWrite',
            db: 'discgenius'
        }]
    }
)
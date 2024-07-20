/*
SQLyog Ultimate v8.55 
MySQL - 8.0.38 : Database - imtiaz
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Data for the table `addresses` */

/*Data for the table `alembic_version` */

insert  into `alembic_version`(`version_num`) values ('165b091b7ccd');

/*Data for the table `brands` */

insert  into `brands`(`id`,`brand_name`,`brand_slug`,`guid`,`created_by`,`created_at`,`status`) values (1,'J.J','jj','893b5b31-f6e8-45ed-9e90-2d12b9703eda',1,'2024-07-18 04:34:47',1),(2,'Nike','nike','83e331f1-e130-4ed6-aa7f-cb35b50e24be',1,'2024-07-18 04:34:47',1),(3,'Dinners','dinners','b3da3cf4-7727-4486-ad31-f89bb28e6de8',1,'2024-07-18 04:34:47',1),(4,'Bata','bata','d0accc23-d359-4412-8811-c23198a36c58',1,'2024-07-18 04:34:47',1),(5,'Gul Ahmed','gul-ahmed','d451122f-0830-4585-a173-d0e1dc565e7f',1,'2024-07-18 04:34:47',1),(6,'Oxfort','oxfort','a3407e02-9cab-41ad-9196-d322910521b6',1,'2024-07-18 04:34:47',1);

/*Data for the table `categories` */

insert  into `categories`(`id`,`parent_id`,`category_name`,`category_slug`,`guid`,`created_by`,`created_at`,`status`) values (1,0,'Man','man','08e13060-635b-4bf3-ac0e-2fee6d4de4fa',1,'2024-07-18 04:34:49',1),(2,0,'Women','women','2f1a05ea-92f6-4d75-a64e-424e2a99d424',1,'2024-07-18 04:34:49',1),(3,0,'Kids','kids','29667dd4-bb09-43e0-be03-10a19834a722',1,'2024-07-18 04:34:49',1),(4,1,'Cloths','cloths','38782729-3cce-4c5d-9e80-5aed4fadec7c',1,'2024-07-18 04:34:49',1),(5,2,'Cloths','cloths','5a99e7df-53a9-4971-bca1-10aa9b390118',1,'2024-07-18 04:34:49',1),(6,3,'Cloths','cloths','bdbeb744-cf5a-48ce-8c31-9cad381dec0b',1,'2024-07-18 04:34:49',1),(7,1,'Shoes','shoes','71670012-4027-4159-a7cb-23c841c2ec5e',1,'2024-07-18 04:34:49',1),(8,1,'Jackets','jackets','917b8f92-1367-49eb-91de-3a8bf49a8030',1,'2024-07-18 04:34:49',1);

/*Data for the table `order_detail` */

insert  into `order_detail`(`id`,`order_guid`,`order_id`,`product_id`,`quantity`,`unit_price`,`discount`,`total_price`,`create_date`,`update_date`,`status`) values (1,'10645f3b-c2b8-47e2-acf9-1db5415bea0e',1,1,1,'3500.00','500.00','3000.00','2024-07-18 04:34:48','2024-07-18 04:34:48',1),(2,'10645f3b-c2b8-47e2-acf9-1db5415bea0e',1,2,2,'4500.00','500.00','8000.00','2024-07-18 04:34:48','2024-07-18 04:34:48',1),(3,'9c0c5ea1-c426-424b-94c1-b45a762b9888',2,2,1,'3000.00','500.00','2500.00','2024-07-18 04:34:48','2024-07-18 04:34:48',1),(4,'9c0c5ea1-c426-424b-94c1-b45a762b9888',2,5,2,'3500.00','0.00','7000.00','2024-07-18 04:34:48','2024-07-18 04:34:48',1),(5,'77c1d11e-877f-48be-9fac-ced4e0369b2e',3,2,1,'3000.00','500.00','2500.00','2024-07-18 07:49:30','2024-07-18 07:49:30',1),(6,'77c1d11e-877f-48be-9fac-ced4e0369b2e',3,5,2,'3500.00','0.00','7000.00','2024-07-18 07:49:30','2024-07-18 07:49:30',1);

/*Data for the table `orders` */

insert  into `orders`(`order_id`,`customer_id`,`total_amount`,`status`,`created_at`,`order_date`,`shipping_address`,`billing_address`,`payment_method`,`guid`,`payment_status`,`delivery_date`,`delivery_status`,`order_status`) values (1,1,'11000.00',1,'2024-07-18 04:34:48','2024-07-18 04:34:48','FB AREA','FB Area','card','10645f3b-c2b8-47e2-acf9-1db5415bea0e','paid',NULL,'pending','created'),(2,1,'9500.00',1,'2024-07-18 04:34:48','2024-07-18 04:34:48','FB AREA, The Comforts','FB Area, The Comforts','card','9c0c5ea1-c426-424b-94c1-b45a762b9888','unpaid',NULL,'pending','created'),(3,1,'9500.00',1,'2024-07-18 07:49:30','2024-07-18 07:49:30','FB AREA, The Comforts','FB Area, The Comforts','card','77c1d11e-877f-48be-9fac-ced4e0369b2e','unpaid',NULL,'pending','created');

/*Data for the table `payments` */

insert  into `payments`(`id`,`order_id`,`customer_id`,`transaction_id`,`payment_gateway`,`amount`,`payment_date`,`status`) values (1,1,1,'80022244231','authorize.net',17,'2024-07-19 14:31:07',1);

/*Data for the table `products` */

insert  into `products`(`id`,`name`,`description`,`price`,`stock_quantity`,`category_id`,`brand_id`,`image_name`,`guid`,`status`,`created_at`,`created_by`) values (1,'Nike Sports Shoes',NULL,'10000.00',10,7,2,NULL,'8ac75044-0034-4730-b7a2-35aeed6485e1',1,'2024-07-18 04:34:45',1),(2,'Bata Formal Shoes',NULL,'3000.00',100,7,4,NULL,'3024858e-b29a-435c-b233-ed5d824738f4',1,'2024-07-18 04:34:45',1),(3,'Bata Casual Shoes',NULL,'4000.00',50,7,4,NULL,'11b230ad-32cb-4b30-a930-58eaa15c4884',1,'2024-07-18 04:34:45',1),(4,'Shalwa Qameez',NULL,'6500.00',50,4,1,NULL,'e9bc57a2-c2a4-4dec-b97d-efaa9a4bddae',1,'2024-07-18 04:34:45',1),(5,'T-Shirts',NULL,'3500.00',50,4,3,NULL,'8de2c2e0-50b6-42d7-8355-e9709f67daf8',1,'2024-07-18 04:34:45',1),(6,'Formall Shirts',NULL,'4500.00',50,4,3,NULL,'9cef080d-d9c8-4590-9a9e-7bf665f9a324',1,'2024-07-18 04:34:45',1),(7,'Pants',NULL,'6000.00',50,4,3,NULL,'c8e0ae8d-3f38-46f4-93da-698855cc8882',1,'2024-07-18 04:34:45',1);

/*Data for the table `shoppingcart` */

/*Data for the table `users` */

insert  into `users`(`id`,`username`,`email`,`password`,`first_name`,`last_name`,`address`,`phone_number`,`guid`,`status`,`created_at`) values (1,'bilalmk','bilalmk@gmail.com','$2b$12$9I1LZUhfXy2O3iCBn41niuSUS6X/q/VHcPV9vOujSlUqfesJi9wSe','Bilal','Khan','FB Area','0321-7001054','0830f793-6a60-49e2-809f-b0bccb5a503e',1,'2024-07-12 11:47:20');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
